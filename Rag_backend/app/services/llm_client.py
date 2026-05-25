from __future__ import annotations

import sys
from typing import Generator

from openai import OpenAI

from app.config import settings


class LLMClient:
    def __init__(self) -> None:
        self.config = settings.llm

        # DeepSeek for chat
        self.chat_client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
        )

        # Embedding client (may use a different provider)
        self.embed_client = OpenAI(
            api_key=self.config.embedding_api_key or self.config.api_key,
            base_url=self.config.embedding_base_url or self.config.base_url,
            timeout=self.config.timeout_seconds,
        )

    @property
    def configured(self) -> bool:
        return bool(self.config.api_key)

    def embed(self, text: str) -> list[float]:
        vectors = self.embed_batch([text])
        return vectors[0] if vectors else []

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.embed_client.embeddings.create(
            model=self.config.embedding_model,
            input=texts
        )
        items = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in items]

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self.config.api_key:
            raise RuntimeError("请先配置 DEEPSEEK_API_KEY。")

        kwargs = {}
        if "deepseek-v4" in self.config.chat_model.lower():
            kwargs["reasoning_effort"] = "high"
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        response = self.chat_client.chat.completions.create(
            model=self.config.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        return response.choices[0].message.content.strip()

    def chat_stream(self, system_prompt: str, user_prompt: str) -> Generator[str, None, None]:
        """Stream chat response token by token."""
        if not self.config.api_key:
            raise RuntimeError("请先配置 DEEPSEEK_API_KEY。")

        kwargs = {}
        if "deepseek-v4" in self.config.chat_model.lower():
            kwargs["reasoning_effort"] = "high"
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}

        stream = self.chat_client.chat.completions.create(
            model=self.config.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
