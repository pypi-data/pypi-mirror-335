from dataclasses import dataclass
from functools import cached_property
from typing import Generic, Sequence

from .source import SourceType
from .statement import Statement
from .verdict import Verdict


@dataclass(frozen=True)
class Ruling(Generic[SourceType]):
    """The result of judging a claim."""

    statements: Sequence[Statement[SourceType]]
    """The constituents of the claim, judged individually."""

    @cached_property
    def verdict(self) -> Verdict:
        """
        Whether the sources support the claim as a whole.
        Note that this is very conservative right now, and will return `NOT_ENOUGH_INFO` more often than not.
        This behavior will be improved in a future release.
        """

        if all(statement.verdict == Verdict.SUPPORTS for statement in self.statements):
            return Verdict.SUPPORTS

        if any(statement.verdict == Verdict.REFUTES for statement in self.statements):
            return Verdict.REFUTES

        return Verdict.NOT_ENOUGH_INFO
