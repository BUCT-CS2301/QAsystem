from dataclasses import dataclass, field
from typing import Any


@dataclass
class Artifact:
    object_id: str
    title: str
    description: str = ""
    period: str = ""
    material: str = ""
    artifact_type: str = ""
    museum: str = ""
    dimensions: str = ""
    image_url: str = ""
    accession_number: str = ""
    score: float = 0.0


@dataclass
class Intent:
    name: str
    attribute: str | None = None
    keywords: list[str] = field(default_factory=list)


@dataclass
class Source:
    type: str
    title: str
    object_id: str = ""
    detail: str = ""


@dataclass
class QAResult:
    question: str
    answer: str
    confidence: float
    sources: list[Source] = field(default_factory=list)
    related_artifacts: list[Artifact] = field(default_factory=list)
    debug: dict[str, Any] = field(default_factory=dict)

    def to_console_text(self) -> str:
        lines = [
            "回答：",
            self.answer,
            "",
            f"置信度：{self.confidence:.2f}",
        ]

        if self.sources:
            lines.append("")
            lines.append("来源：")
            for idx, source in enumerate(self.sources, 1):
                suffix = f" - {source.detail}" if source.detail else ""
                object_id = f" ({source.object_id})" if source.object_id else ""
                lines.append(f"{idx}. [{source.type}] {source.title}{object_id}{suffix}")

        if self.related_artifacts:
            lines.append("")
            lines.append("相关文物：")
            for idx, artifact in enumerate(self.related_artifacts[:8], 1):
                reason = []
                if artifact.period:
                    reason.append(f"时期：{artifact.period}")
                if artifact.material:
                    reason.append(f"材质：{artifact.material}")
                if artifact.artifact_type:
                    reason.append(f"品类：{artifact.artifact_type}")
                reason_text = "；".join(reason)
                lines.append(f"{idx}. {artifact.title} ({artifact.object_id}) {reason_text}")

        return "\n".join(lines)
