from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

import httpx

from .errors import APIError
from .parse_response import parse_response
from .ruling import Ruling
from .source import SourceType

DEFAULT_TIMEOUT_SECONDS = 30
JUDGE_ROUTE = "/api/get_context_output"


@dataclass(frozen=True)
class Client:
    _httpx_client: httpx.Client

    @classmethod
    def from_url(cls, base_url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        return cls(httpx.Client(base_url=base_url, timeout=timeout))

    @classmethod
    def from_httpx(cls, client: httpx.Client):
        return cls(client)

    def judge(self, claim: str, sources: Iterable[SourceType]) -> Ruling[SourceType]:
        """Assess the veracity of a claim based on the sources."""

        source_list = list(sources)  # in case sources is a generator
        try:
            response = self._httpx_client.post(
                JUDGE_ROUTE,
                json=_build_request_payload(claim, source_list),
            )
        except Exception as e:
            raise APIError("Failed to connect to Truth Systems API") from e

        if response.status_code != 200:
            raise APIError(_generate_error_message(response))

        return parse_response(response, sources=source_list)


@dataclass(frozen=True)
class AsyncClient:
    _httpx_client: httpx.AsyncClient

    @classmethod
    def from_url(cls, base_url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        return cls(httpx.AsyncClient(base_url=base_url, timeout=timeout))

    @classmethod
    def from_httpx(cls, client: httpx.AsyncClient):
        return cls(client)

    async def judge(
        self, claim: str, sources: Iterable[SourceType]
    ) -> Ruling[SourceType]:
        """Assess the veracity of a claim based on the sources."""

        source_list = list(sources)  # in case sources is a generator
        try:
            response = await self._httpx_client.post(
                JUDGE_ROUTE,
                json=_build_request_payload(claim, source_list),
            )
        except Exception as e:
            raise APIError("Failed to connect to Truth Systems API") from e

        if response.status_code != 200:
            raise APIError(_generate_error_message(response))

        return parse_response(response, sources=source_list)


def _build_request_payload(claim: str, source_list: List[SourceType]):
    return {
        "params": {
            "claim": claim,
            "sources": _serialize_sources(source_list),
        }
    }


def _serialize_sources(source_list: List[SourceType]):
    counter = Counter(source.id for source in source_list)
    duplicates = [id for id, count in counter.items() if count > 1]
    if len(duplicates) > 1:
        duplicate_names = ", ".join(duplicates)
        raise ValueError(f"Duplicate source IDs found: {duplicate_names}")

    return [source._serialized for source in source_list]


def _generate_error_message(response: httpx.Response) -> str:
    error_message = f"Truth Systems API responded with {response.status_code}"

    try:
        response_json = response.json()
        if "error" in response_json:
            error_message += f": {response_json['error']}"
        if "details" in response_json:
            error_message += f" ({response_json['details']})"
    except Exception:
        pass

    return error_message
