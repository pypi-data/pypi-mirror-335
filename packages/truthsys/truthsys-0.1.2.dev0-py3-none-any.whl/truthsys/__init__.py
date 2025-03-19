"""
SDK for the Truth Systems API - https://truthsystems.ai

The SDK allows you to submit a claim and sources to verify that claim against.
It returns a ruling on the claim - whether it is supported by the sources or not - and identify the sources that influenced the ruling.

For more details, check the README.
"""

from ._version import __version__
from .client import AsyncClient, Client
from .influence import Influence, TextInfluence
from .ruling import Ruling
from .source import Source, TextSource
from .statement import Statement
from .verdict import Verdict

__all__ = [
    "__version__",
    "AsyncClient",
    "Client",
    "Influence",
    "TextInfluence",
    "Ruling",
    "Source",
    "TextSource",
    "Statement",
    "Verdict",
]
