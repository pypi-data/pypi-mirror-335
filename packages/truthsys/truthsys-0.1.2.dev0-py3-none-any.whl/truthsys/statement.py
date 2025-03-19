from dataclasses import dataclass
from typing import Generic, Sequence, Tuple

from .influence import Influence
from .source import SourceType
from .verdict import Verdict


@dataclass(frozen=True)
class Statement(Generic[SourceType]):
    """A single statement made as part of the claim."""

    text: str
    """
    Not necessarily a substring of the claim - e.g. "The sky is blue." could be a statement from the claim "The sky is clear and blue."
    """

    span: Tuple[int, int]
    """`claim[span[0]:span[1]]` is the substring of the claim that corresponds to this statement."""

    verdict: Verdict
    """Whether this statement is supported by the sources or not."""

    influences: Sequence[Influence[SourceType]]
    """The source statements that influenced the verdict."""
