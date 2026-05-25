import hashlib
import json
from typing import Any

from app.config import settings


class CacheService:
    def __init__(self) -> None:
        self.client = None
        if not settings.redis.enabled:
            return
        try:
            import redis

            self.client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            self.client.ping()
        except Exception:
            self.client = None

    def make_question_key(self, question: str) -> str:
        normalized = self.normalize_question(question)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        return f"qa:answer:{digest}"

    def normalize_question(self, question: str) -> str:
        return " ".join(question.strip().lower().split())

    def get_json(self, key: str) -> dict[str, Any] | None:
        if not self.client:
            return None
        try:
            raw = self.client.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    def set_json(self, key: str, value: dict[str, Any]) -> None:
        if not self.client:
            return
        try:
            self.client.setex(key, settings.redis.ttl_seconds, json.dumps(value, ensure_ascii=False))
        except Exception:
            return

    def remember_question(self, question: str, answer: str) -> None:
        if not self.client:
            return
        try:
            item = json.dumps(
                {
                    "question": question.strip(),
                    "answer": answer[:500],
                },
                ensure_ascii=False,
            )
            self.client.lpush("qa:history", item)
            self.client.ltrim("qa:history", 0, settings.redis.history_limit - 1)
        except Exception:
            return
