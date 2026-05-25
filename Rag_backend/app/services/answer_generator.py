import sys
from typing import Generator

from app.models import Artifact, Intent, QAResult, Source
from app.config import settings
from app.services.llm_client import LLMClient


ATTRIBUTE_LABELS = {
    "material": "材质",
    "period": "时期/朝代",
    "type": "品类",
    "museum": "馆藏博物馆",
    "image": "图片",
    "dimensions": "尺寸",
    "description": "描述",
    "accession_number": "藏品编号",
}

RAG_SYSTEM_PROMPT = (
    "你是一位博物馆知识问答系统的资深中文讲解员。\n"
    "你只能依据用户给出的【已知文物知识库文档】里的信息来回答，不能编造数据库中没有的信息。\n"
    "你的回答必须包含两个部分，并使用 [CONTENT] 和 [LLM_CONTENT] 标签分隔：\n"
    "1. [CONTENT] 部分：直接、简洁地回答用户问题（50字以内）；\n"
    "2. [LLM_CONTENT] 部分：相关文物的详细讲解（不少于200字），涵盖朝代、材质、品类、博物馆、尺寸及历史积淀等信息。\n"
    "格式示例：\n"
    "[CONTENT]\n"
    "《清明上河图》现藏于北京故宫博物院。\n"
    "[LLM_CONTENT]\n"
    "《清明上河图》是北宋画家张择端的代表作..."
)


class AnswerGenerator:
    def __init__(self) -> None:
        self.llm = LLMClient()

    # ── Streaming RAG answer (preferred for console) ──────────────────

    def build_rag_answer_stream(
        self, question: str, artifacts: list[Artifact]
    ) -> tuple[Generator[str, None, None], "QAResultMeta"]:
        """Return a (token_generator, metadata) pair.

        The caller should iterate over token_generator to print tokens in
        real-time, then use metadata to build the final QAResult.
        """
        if not artifacts:
            result = self.build_no_result(question)
            return iter([result.answer]), QAResultMeta.from_result(result)

        top_score = artifacts[0].score
        if top_score < settings.rag.min_score:
            fallback_answer = "当前数据库中暂无记录。请换一种问法，或补充文物名称、朝代、材质、品类、馆藏等线索。"
            meta = QAResultMeta(
                question=question,
                confidence=max(0.1, min(top_score, 0.45)),
                sources=self._deduplicated_sources(artifacts[:3]),
                related_artifacts=self._deduplicated_artifacts(artifacts[:5]),
                debug={"top_score": top_score, "rejected_by_min_score": settings.rag.min_score},
            )
            return iter([fallback_answer]), meta

        prompt = self._build_rag_prompt(question, artifacts)
        meta = QAResultMeta(
            question=question,
            confidence=self._score_to_confidence(top_score),
            sources=self._deduplicated_sources(artifacts[:5]),
            related_artifacts=self._deduplicated_artifacts(artifacts[:8]),
            debug={"top_score": top_score, "llm_used": self.llm.configured},
        )

        try:
            token_gen = self.llm.chat_stream(
                system_prompt=RAG_SYSTEM_PROMPT,
                user_prompt=prompt,
            )
        except Exception as exc:
            fallback = self._build_extract_answer(question, artifacts)
            meta.debug["llm_error"] = str(exc)
            return iter([fallback]), meta

        return token_gen, meta

    # ── Non-streaming RAG answer (for caching / API) ──────────────────

    def build_rag_answer(self, question: str, artifacts: list[Artifact]) -> QAResult:
        if not artifacts:
            return self.build_no_result(question)

        top_score = artifacts[0].score
        if top_score < settings.rag.min_score:
            return QAResult(
                question=question,
                content="当前数据库中暂无记录。请换一种问法，或补充文物名称、朝代、材质、品类、馆藏等线索。",
                llmContent="",
                confidence=max(0.1, min(top_score, 0.45)),
                sources=self._deduplicated_sources(artifacts[:3]),
                related_artifacts=self._deduplicated_artifacts(artifacts[:5]),
                debug={"top_score": top_score, "rejected_by_min_score": settings.rag.min_score},
            )

        prompt = self._build_rag_prompt(question, artifacts)
        try:
            answer = self.llm.chat(
                system_prompt=RAG_SYSTEM_PROMPT,
                user_prompt=prompt,
            )
        except Exception as exc:
            answer = self._build_extract_answer(question, artifacts)
            return QAResult(
                question=question,
                content=answer,
                llmContent="",
                confidence=self._score_to_confidence(top_score),
                sources=self._deduplicated_sources(artifacts[:5]),
                related_artifacts=self._deduplicated_artifacts(artifacts[:8]),
                debug={"top_score": top_score, "llm_error": str(exc)},
            )

        if not answer:
            answer = self._build_extract_answer(question, artifacts)

        content, llm_content = self._split_answer(answer)

        return QAResult(
            question=question,
            content=content,
            llmContent=llm_content,
            confidence=self._score_to_confidence(top_score),
            sources=self._deduplicated_sources(artifacts[:5]),
            related_artifacts=self._deduplicated_artifacts(artifacts[:8]),
            debug={"top_score": top_score, "llm_used": self.llm.configured},
        )

    # ── Other answer builders ─────────────────────────────────────────

    def build_no_result(self, question: str) -> QAResult:
        return QAResult(
            question=question,
            content="当前数据库中没有检索到足够明确的文物或图谱关系。可以尝试补充文物名称、朝代、材质、品类或博物馆名称。",
            llmContent="",
            confidence=0.2,
        )

    def build_attribute_answer(
        self,
        question: str,
        intent: Intent,
        artifact: Artifact,
        related: list[Artifact] | None = None,
    ) -> QAResult:
        attribute = intent.attribute or "description"
        value = self._get_attribute_value(artifact, attribute)
        label = ATTRIBUTE_LABELS.get(attribute, "信息")

        if value:
            answer = f"{artifact.title}的{label}是：{value}。"
            confidence = 0.86
        else:
            answer = f"当前数据库中暂无{artifact.title}的{label}明确记录。"
            confidence = 0.45

        if attribute == "description" and artifact.description:
            answer = self._build_intro(artifact)

        return QAResult(
            question=question,
            content=answer,
            llmContent="",
            confidence=confidence,
            sources=[self._source_from_artifact(artifact, label)],
            related_artifacts=related or [],
        )

    def build_list_answer(self, question: str, artifacts: list[Artifact]) -> QAResult:
        if not artifacts:
            return self.build_no_result(question)

        lines = [f"根据图谱检索，找到 {len(artifacts)} 件较相关的文物："]
        for idx, artifact in enumerate(artifacts, 1):
            tags = []
            if artifact.period:
                tags.append(artifact.period)
            if artifact.material:
                tags.append(artifact.material)
            if artifact.artifact_type:
                tags.append(artifact.artifact_type)
            tag_text = f"（{'；'.join(tags)}）" if tags else ""
            lines.append(f"{idx}. {artifact.title}{tag_text}")

        return QAResult(
            question=question,
            content="\n".join(lines),
            llmContent="",
            confidence=0.76,
            sources=[self._source_from_artifact(item, "图谱匹配") for item in artifacts[:5]],
            related_artifacts=artifacts[:8],
        )

    def build_related_answer(self, question: str, artifact: Artifact, related: list[Artifact]) -> QAResult:
        if not related:
            return QAResult(
                question=question,
                content=f'已识别到文物"{artifact.title}"，但当前图谱中没有找到明显共享关系的相关文物。',
                llmContent="",
                confidence=0.55,
                sources=[self._source_from_artifact(artifact, "目标文物")],
            )

        lines = [f'与"{artifact.title}"较相关的文物主要有：']
        for idx, item in enumerate(related[:8], 1):
            reasons = []
            if item.period:
                reasons.append(f"时期 {item.period}")
            if item.material:
                reasons.append(f"材质 {item.material}")
            if item.artifact_type:
                reasons.append(f"品类 {item.artifact_type}")
            reason_text = f"，关联依据：{'；'.join(reasons)}" if reasons else ""
            lines.append(f"{idx}. {item.title}{reason_text}")

        return QAResult(
            question=question,
            content="\n".join(lines),
            llmContent="",
            confidence=0.78,
            sources=[self._source_from_artifact(artifact, "目标文物")],
            related_artifacts=related,
        )

    def build_general_answer(self, question: str, artifact: Artifact, related: list[Artifact]) -> QAResult:
        answer = self._build_intro(artifact)
        return QAResult(
            question=question,
            content=answer,
            llmContent="",
            confidence=0.8,
            sources=[self._source_from_artifact(artifact, "文物详情")],
            related_artifacts=related[:5],
        )

    # ── Private helpers ───────────────────────────────────────────────

    def _build_intro(self, artifact: Artifact) -> str:
        parts = [f'"{artifact.title}"是当前数据库中的一件文物。']
        if artifact.period:
            parts.append(f"它的时期/朝代记录为：{artifact.period}。")
        if artifact.material:
            parts.append(f"材质记录为：{artifact.material}。")
        if artifact.artifact_type:
            parts.append(f"品类记录为：{artifact.artifact_type}。")
        if artifact.museum:
            parts.append(f"馆藏博物馆为：{artifact.museum}。")
        if artifact.dimensions:
            parts.append(f"尺寸信息为：{artifact.dimensions}。")
        if artifact.description:
            parts.append(f"简介：{artifact.description[:500]}")
        return "\n".join(parts)

    def _get_attribute_value(self, artifact: Artifact, attribute: str) -> str:
        mapping = {
            "material": artifact.material,
            "period": artifact.period,
            "type": artifact.artifact_type,
            "museum": artifact.museum,
            "image": artifact.image_url,
            "dimensions": artifact.dimensions,
            "description": artifact.description,
            "accession_number": artifact.accession_number,
        }
        return mapping.get(attribute, "")

    def _source_from_artifact(self, artifact: Artifact, detail: str) -> Source:
        # 优先使用博物馆官网作为来源，如果没有则使用外部链接或占位符
        return Source(
            name=artifact.museum or "博物馆知识图谱",
            url=artifact.image_url or "https://www.dpm.org.cn/",  # 默认指向故宫
        )

    def _deduplicated_sources(self, artifacts: list[Artifact]) -> list[Source]:
        """Generate sources list with deduplication by object_id."""
        seen: set[str] = set()
        sources: list[Source] = []
        for item in artifacts:
            if item.object_id in seen:
                continue
            seen.add(item.object_id)
            sources.append(self._source_from_artifact(item, f"相似度 {item.score:.3f}"))
        return sources

    def _deduplicated_artifacts(self, artifacts: list[Artifact]) -> list[Artifact]:
        """Deduplicate artifacts by object_id, keeping the first (highest score) occurrence."""
        seen: set[str] = set()
        result: list[Artifact] = []
        for item in artifacts:
            if item.object_id in seen:
                continue
            seen.add(item.object_id)
            result.append(item)
        return result

    def _build_rag_prompt(self, question: str, artifacts: list[Artifact]) -> str:
        docs = []
        for idx, artifact in enumerate(artifacts, 1):
            parts = [f"{idx}. [{artifact.title}] (object_id: {artifact.object_id}, score: {artifact.score:.3f})"]
            if artifact.period:
                parts.append(f"   - period: {artifact.period}")
            if artifact.material:
                parts.append(f"   - material: {artifact.material}")
            if artifact.artifact_type:
                parts.append(f"   - type: {artifact.artifact_type}")
            if artifact.museum:
                parts.append(f"   - museum: {artifact.museum}")
            if artifact.dimensions:
                parts.append(f"   - dimensions: {artifact.dimensions}")
            if artifact.accession_number:
                parts.append(f"   - accession_number: {artifact.accession_number}")
            desc = artifact.description or ""
            if desc:
                parts.append(f"   - description: {desc}")
            docs.append("\n".join(parts))
        return (
            "【已知文物知识库文档】\n"
            + "\n\n".join(docs)
            + "\n\n请严格结合上方文档，详细回答用户问题："
            + question
            + "\n回答要求至少200字，尽可能涵盖文档中提到的所有字段信息。"
            + '\n如果上方文档不包含相关信息，请回答"当前数据库中暂无记录"，不要自行补充历史知识。'
        )

    def _build_extract_answer(self, question: str, artifacts: list[Artifact]) -> str:
        lines = ["根据当前知识库，检索到以下最相关的文物记录："]
        for idx, artifact in enumerate(artifacts[:5], 1):
            text = artifact.description.strip()
            if len(text) > 260:
                text = text[:260] + "..."
            lines.append(f"{idx}. {artifact.title}：{text}")
        lines.append("提示：配置大模型后，系统会将这些检索结果进一步整理成自然语言回答。")
        return "\n".join(lines)

    @staticmethod
    def _split_answer_static(text: str) -> tuple[str, str]:
        if "[LLM_CONTENT]" in text:
            parts = text.split("[LLM_CONTENT]")
            content = parts[0].replace("[CONTENT]", "").strip()
            llm_content = parts[1].strip()
            return content, llm_content
        return text, ""

    def _split_answer(self, text: str) -> tuple[str, str]:
        return self._split_answer_static(text)

    def _score_to_confidence(self, score: float) -> float:
        if score >= settings.rag.high_score:
            return 0.92
        if score <= settings.rag.min_score:
            return 0.5
        span = settings.rag.high_score - settings.rag.min_score
        return 0.5 + ((score - settings.rag.min_score) / span) * 0.42

class QAResultMeta:
    """Lightweight metadata container for streaming answers."""

    def __init__(
        self,
        question: str,
        confidence: float,
        sources: list[Source] | None = None,
        related_artifacts: list[Artifact] | None = None,
        debug: dict | None = None,
    ):
        self.question = question
        self.confidence = confidence
        self.sources = sources or []
        self.related_artifacts = related_artifacts or []
        self.debug = debug or {}

    @classmethod
    def from_result(cls, result: QAResult) -> "QAResultMeta":
        return cls(
            question=result.question,
            confidence=result.confidence,
            sources=result.sources,
            related_artifacts=result.related_artifacts,
            debug=result.debug,
        )

    def to_result(self, answer: str) -> QAResult:
        content, llm_content = AnswerGenerator._split_answer_static(answer)
        return QAResult(
            question=self.question,
            content=content,
            llmContent=llm_content,
            confidence=self.confidence,
            sources=self.sources,
            related_artifacts=self.related_artifacts,
            debug=self.debug,
        )
