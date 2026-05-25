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
    name: str
    url: str


@dataclass
class QAResult:
    question: str
    content: str
    llmContent: str
    confidence: float
    sources: list[Source] = field(default_factory=list)
    related_artifacts: list[Artifact] = field(default_factory=list)
    debug: dict[str, Any] = field(default_factory=dict)
