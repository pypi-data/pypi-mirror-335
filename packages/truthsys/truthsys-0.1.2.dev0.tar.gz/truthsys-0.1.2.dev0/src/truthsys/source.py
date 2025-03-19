from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, TypeVar
from uuid import uuid4


@dataclass(frozen=True)
class Source(ABC):
    """A source (e.g. document) that a claim may be based on."""

    id: str

    @cached_property
    @abstractmethod
    def _serialized(self) -> Any:
        """The source in serialized form, ready to send to the API."""


@dataclass(frozen=True)
class TextSource(Source):
    """A plain-text source that a claim may be based on."""

    text: str

    @cached_property
    def _serialized(self) -> Any:
        return {"id": self.id, "text": self.text}

    @classmethod
    def from_text(cls, text: str):
        return cls(str(uuid4()), text=text)


SourceType = TypeVar("SourceType", bound=Source)
