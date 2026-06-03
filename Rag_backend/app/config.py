import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class MySQLConfig:
    host: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    port: int = _int_env("MYSQL_PORT", 3307)
    user: str = os.getenv("MYSQL_USER", "root")
    password: str = os.getenv("MYSQL_PASSWORD", "")
    database: str = os.getenv("MYSQL_DATABASE", "admin_platform")
    charset: str = "utf8mb4"


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    user: str = os.getenv("NEO4J_USER", "neo4j")
    password: str = os.getenv("NEO4J_PASSWORD", "")


@dataclass(frozen=True)
class LLMConfig:
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.siliconflow.cn/v1")
    chat_model: str = os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-ai/DeepSeek-V3")
    
    # 考虑到 DeepSeek 目前可能不支持 embeddings 接口，保留一个独立配置以支持其他模型(如果不填默认会使用上面的Key)
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "")
    embedding_base_url: str = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    
    timeout_seconds: int = _int_env("LLM_TIMEOUT_SECONDS", 60)
    max_tokens: int = _int_env("LLM_MAX_TOKENS", 2048)
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))


@dataclass(frozen=True)
class RAGConfig:
    vector_index_name: str = os.getenv("NEO4J_VECTOR_INDEX", "artifact_vector_index")
    vector_property: str = os.getenv("NEO4J_VECTOR_PROPERTY", "embedding")
    text_property: str = os.getenv("NEO4J_TEXT_PROPERTY", "text")
    result_limit: int = _int_env("QA_RESULT_LIMIT", 12)
    min_score: float = float(os.getenv("QA_MIN_SCORE", "0.6"))
    high_score: float = float(os.getenv("QA_HIGH_SCORE", "0.85"))


@dataclass(frozen=True)
class Settings:
    mysql: MySQLConfig = MySQLConfig()
    neo4j: Neo4jConfig = Neo4jConfig()
    llm: LLMConfig = LLMConfig()
    rag: RAGConfig = RAGConfig()
    result_limit: int = _int_env("QA_RESULT_LIMIT", 12)


settings = Settings()
