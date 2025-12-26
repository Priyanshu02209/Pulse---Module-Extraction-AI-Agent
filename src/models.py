from dataclasses import dataclass, field
from typing import List


@dataclass
class Section:
    level: int
    title: str
    text: str
    children: List["Section"] = field(default_factory=list)


@dataclass
class Submodule:
    name: str
    description: str
    source_urls: List[str]
    confidence: float


@dataclass
class Module:
    name: str
    description: str
    submodules: List[Submodule]
    source_urls: List[str]
    confidence: float


@dataclass
class ExtractionResult:
    modules: List[Module]

