from enum import Enum, auto


# separate from PredictionEnum so that we can have all-caps enum members without changing the API codebase
class Verdict(Enum):
    """Whether a statement is supported by sources."""

    SUPPORTS = auto()
    """The statement is true according to the sources."""

    NOT_ENOUGH_INFO = auto()
    """The statement is not supported by the sources, but it doesn't go against them."""

    REFUTES = auto()
    """The statement goes against the sources."""
