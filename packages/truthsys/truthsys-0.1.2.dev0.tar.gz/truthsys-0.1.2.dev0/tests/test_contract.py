from typing import Awaitable, Callable, List

import pytest
from pytest_httpserver import HTTPServer
from truthsys import AsyncClient, Client, Ruling, TextInfluence, TextSource, Verdict
from truthsys.errors import APIError
from werkzeug import Response


async def run_client(base_url: str, claim: str, sources: List[TextSource]) -> Ruling:
    client = Client.from_url(base_url)
    return client.judge(claim=claim, sources=sources)


async def run_async_client(
    base_url: str, claim: str, sources: List[TextSource]
) -> Ruling:
    client = AsyncClient.from_url(base_url)
    return await client.judge(claim=claim, sources=sources)


@pytest.mark.parametrize("callable", [run_client, run_async_client])
async def test_sally(
    httpserver: HTTPServer,
    callable: Callable[[str, str, List[TextSource]], Awaitable[Ruling]],
):
    """The example from the public README."""

    httpserver.expect_request(
        "/api/get_context_output",
        method="POST",
        json={
            "params": {
                "claim": "Sally is a pretty cat",
                "sources": [
                    {"id": "1", "text": "I have a cat"},
                    {"id": "2", "text": "I only have one pet"},
                    {"id": "3", "text": "My pet is called Sally"},
                ],
            }
        },
    ).respond_with_json(
        {
            "detailed_responses": [
                {
                    "atomic": "Sally is a pretty cat",
                    "prediction": "SUPPORTS",
                    "prediction_num": 2,
                    "prediction_vector": [0.352294921875, 0.0, 0.64794921875],
                    "span": [0, 21],
                    "top5_sentences": [
                        [
                            "My pet is called Sally",
                            "I have a cat",
                            "I only have one pet",
                        ],
                        ["3", "1", "2"],
                        [
                            [4.091995716094971],
                            [2.281024932861328],
                            [-12.288034439086914],
                        ],
                        [[0, 22], [0, 12], [0, 19]],
                    ],
                }
            ],
            "sentences": [
                {
                    "evidence": {
                        "ids": ["3"],
                        "scores": [[4.091995716094971]],
                        "source_spans": [[0, 22]],
                    },
                    "span": [0, 21],
                    "verdict": 2,
                }
            ],
        }
    )

    sources = [
        TextSource(id="1", text="I have a cat"),
        TextSource(id="2", text="I only have one pet"),
        TextSource(id="3", text="My pet is called Sally"),
    ]
    ruling = await callable(httpserver.url_for("/"), "Sally is a pretty cat", sources)

    assert len(ruling.statements) == 1
    statement = ruling.statements[0]

    assert statement.text == "Sally is a pretty cat"
    assert statement.span == (0, 21)
    assert statement.verdict == Verdict.SUPPORTS
    assert len(statement.influences) == 3

    assert isinstance(statement.influences[0], TextInfluence)
    assert statement.influences[0].source is sources[2]
    assert statement.influences[0].text == "My pet is called Sally"
    assert statement.influences[0].span == (0, 22)

    assert isinstance(statement.influences[1], TextInfluence)
    assert statement.influences[1].source is sources[0]
    assert statement.influences[1].text == "I have a cat"
    assert statement.influences[1].span == (0, 12)

    assert isinstance(statement.influences[2], TextInfluence)
    assert statement.influences[2].source is sources[1]
    assert statement.influences[2].text == "I only have one pet"
    assert statement.influences[2].span == (0, 19)


@pytest.mark.parametrize("callable", [run_client, run_async_client])
@pytest.mark.parametrize("status_code", [400, 500])
async def test_error_codes(
    httpserver: HTTPServer,
    callable: Callable[[str, str, List[TextSource]], Awaitable[Ruling]],
    status_code: int,
):
    """The example from the public README."""

    httpserver.expect_request(
        "/api/get_context_output", method="POST"
    ).respond_with_response(Response(status=status_code))

    sources = [
        TextSource(id="1", text="I have a cat"),
        TextSource(id="2", text="I only have one pet"),
        TextSource(id="3", text="My pet is called Sally"),
    ]
    with pytest.raises(APIError):
        await callable(httpserver.url_for("/"), "Sally is a pretty cat", sources)
