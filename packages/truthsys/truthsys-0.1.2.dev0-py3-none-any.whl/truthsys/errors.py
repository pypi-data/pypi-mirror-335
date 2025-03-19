"""Exceptions specific to the Truth Systems API."""


class APIError(Exception):
    """An error in communicating with the Truth Systems API."""


class VersionMismatchError(APIError):
    """The SDK and API versions are incompatible."""
