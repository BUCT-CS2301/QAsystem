from dataclasses import asdict

from neo4j.exceptions import Neo4jError, ServiceUnavailable
from pymysql.err import MySQLError
from requests import RequestException

from app.config import settings
from app.db import Database
from app.models import Artifact, QAResult, Source
from app.services.answer_generator import AnswerGenerator, QAResultMeta
from app.services.cache_service import CacheService
from app.services.llm_client import LLMClient
from app.services.graph_retriever import GraphRetriever
from app.services.mysql_retriever import MySQLRetriever
from typing import Generator


class QAService:
    def __init__(self) -> None:
        self.db = Database()
        self.graph = GraphRetriever(self.db.neo4j)
        self.mysql = MySQLRetriever(self.db)
        self.llm = LLMClient()
        self.answer_generator = AnswerGenerator()
        self.cache = CacheService()

    def ask(self, question: str) -> QAResult:
        cache_key = self.cache.make_question_key(question)
        cached = self.cache.get_json(cache_key)
        if cached:
            result = self._result_from_dict(cached)
            result.debug["cache_hit"] = True
            return result

        try:
            query_vector = self.llm.embed(question)
            artifacts = self.graph.vector_search(query_vector, settings.rag.result_limit)
            artifacts = [self._merge_mysql(item) for item in artifacts]
            result = self.answer_generator.build_rag_answer(question, artifacts)
        except (ServiceUnavailable, Neo4jError) as exc:
            result = QAResult(
                question=question,
                content=(
                    "当前无法连接 Neo4j 图数据库，或向量索引尚未创建。"
                    "请确认 dev-neo4j 容器已启动，并先运行 scripts/embed_artifacts.py。"
                ),
                llmContent="",
                confidence=0.0,
                debug={"error": str(exc)},
            )
        except MySQLError as exc:
            result = QAResult(
                question=question,
                content="当前无法连接 MySQL 数据库，请确认 dev-mysql 容器已经启动，并且 127.0.0.1:3307 可以访问。",
                llmContent="",
                confidence=0.0,
                debug={"error": str(exc)},
            )
        except (RequestException, RuntimeError) as exc:
            result = QAResult(
                question=question,
                content=(
                    "当前无法调用 Embedding/Chat API。请在统一配置中填写 DEEPSEEK_API_KEY 等参数后重试。"
                ),
                llmContent="",
                confidence=0.0,
                debug={"error": str(exc)},
            )

        if result.confidence > 0:
            self.cache.set_json(cache_key, asdict(result))
            self.cache.remember_question(question, result.content)
        return result

    def ask_stream(self, question: str) -> tuple[Generator[str, None, None], QAResultMeta]:
        cache_key = self.cache.make_question_key(question)
        cached = self.cache.get_json(cache_key)
        if cached:
            result = self._result_from_dict(cached)
            result.debug["cache_hit"] = True
            meta = QAResultMeta.from_result(result)
            return iter([result.content]), meta

        try:
            query_vector = self.llm.embed(question)
            artifacts = self.graph.vector_search(query_vector, settings.rag.result_limit)
            artifacts = [self._merge_mysql(item) for item in artifacts]
            token_gen, meta = self.answer_generator.build_rag_answer_stream(question, artifacts)

            def wrap_generator(gen: Generator[str, None, None]) -> Generator[str, None, None]:
                full_answer = []
                for token in gen:
                    full_answer.append(token)
                    yield token
                answer_str = "".join(full_answer)
                if meta.confidence > 0:
                    final_result = meta.to_result(answer_str)
                    self.cache.set_json(cache_key, asdict(final_result))
                    self.cache.remember_question(question, answer_str)

            return wrap_generator(token_gen), meta

        except (ServiceUnavailable, Neo4jError) as exc:
            answer = (
                "当前无法连接 Neo4j 图数据库，或向量索引尚未创建。"
                "请确认 dev-neo4j 容器已启动，并先运行 scripts/embed_artifacts.py。"
            )
            meta = QAResultMeta(question=question, confidence=0.0, debug={"error": str(exc)})
            return iter([answer]), meta
        except MySQLError as exc:
            answer = "当前无法连接 MySQL 数据库，请确认 dev-mysql 容器已经启动，并且 127.0.0.1:3307 可以访问。"
            meta = QAResultMeta(question=question, confidence=0.0, debug={"error": str(exc)})
            return iter([answer]), meta
        except (RequestException, RuntimeError) as exc:
            answer = "当前无法调用 Embedding/Chat API。请在统一配置中填写 DEEPSEEK_API_KEY 等参数后重试。"
            meta = QAResultMeta(question=question, confidence=0.0, debug={"error": str(exc)})
            return iter([answer]), meta

    def close(self) -> None:
        self.db.close()

    def _merge_mysql(self, artifact: Artifact) -> Artifact:
        mysql_artifact = self.mysql.get_artifact(artifact.object_id)
        if not mysql_artifact:
            return artifact
        return Artifact(
            object_id=artifact.object_id or mysql_artifact.object_id,
            title=artifact.title or mysql_artifact.title,
            description=artifact.description or mysql_artifact.description,
            period=mysql_artifact.period,
            material=mysql_artifact.material,
            artifact_type=mysql_artifact.artifact_type,
            museum=mysql_artifact.museum,
            dimensions=mysql_artifact.dimensions or artifact.dimensions,
            image_url=mysql_artifact.image_url,
            accession_number=mysql_artifact.accession_number or artifact.accession_number,
            score=artifact.score,
        )

    def _result_from_dict(self, data: dict) -> QAResult:
        sources = [Source(**item) for item in data.get("sources", [])]
        related = [Artifact(**item) for item in data.get("related_artifacts", [])]
        return QAResult(
            question=data.get("question", ""),
            content=data.get("content", ""),
            llmContent=data.get("llmContent", ""),
            confidence=float(data.get("confidence", 0)),
            sources=sources,
            related_artifacts=related,
            debug=data.get("debug", {}),
        )
