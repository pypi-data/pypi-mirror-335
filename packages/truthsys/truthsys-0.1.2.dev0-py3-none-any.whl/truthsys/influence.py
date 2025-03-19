from abc import ABC
from dataclasses import dataclass
from typing import Generic, Tuple

from .source import SourceType, TextSource


@dataclass(frozen=True)
class Influence(ABC, Generic[SourceType]):
    """One statement made in a source."""

    source: SourceType
    """The source that the sentence is from."""

    text: str
    """This atomic phrased as a statement."""


@dataclass(frozen=True)
class TextInfluence(Influence[TextSource]):
    """A statement made in a plain-text source."""

    span: Tuple[int, int]
    """`source.text[span[0]:span[1]]` gives the text of this sentence."""
