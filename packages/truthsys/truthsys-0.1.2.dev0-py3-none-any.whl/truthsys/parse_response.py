from typing import NoReturn, Sequence, Tuple

from httpx import Response

from .errors import APIError, VersionMismatchError
from .influence import Influence, TextInfluence
from .ruling import Ruling
from .schemas import HallucinationDetectionResponse, PredictionEnum
from .source import SourceType, TextSource
from .statement import Statement
from .verdict import Verdict


def parse_response(
    response: Response, sources: Sequence[SourceType]
) -> Ruling[SourceType]:
    try:
        json = response.json()
    except Exception as e:
        raise APIError("Truth Systems API returned invalid JSON") from e

    return _parse_ruling(json, sources=sources)


def _parse_ruling(response, sources: Sequence[SourceType]) -> Ruling[SourceType]:
    if isinstance(response, dict) and "version" in response:
        raise VersionMismatchError(
            "The SDK version is behind that of the API. Update the truthsys package."
        )

    try:
        return Ruling(
            statements=[
                _parse_statement(atomic, sources=sources)
                for atomic in response["detailed_responses"]
            ]
        )
    except Exception as e:
        raise APIError(
            "Failed to parse response from Truth Systems API. Please let us know."
        ) from e


def _parse_statement(response, sources: Sequence[SourceType]) -> Statement[SourceType]:
    validated = HallucinationDetectionResponse.model_validate(response)

    source_id_to_source = {source.id: source for source in sources}

    def make_influence(
        source_id: str, text: str, span: Tuple[int, int]
    ) -> Influence[SourceType]:
        found_source = source_id_to_source[source_id]
        if not isinstance(found_source, TextSource):
            raise TypeError(
                f"The only supported source type is TextSource, but found a {type(found_source)} with ID {source_id}"
            )

        result: TextInfluence = TextInfluence(
            source=found_source,
            text=text,
            span=span,
        )
        # we know that SourceType is actually always TextSource for now
        # but we don't want the SDK users to rely on it, so the type checker doesn't know
        return result  # type: ignore

    return Statement(
        text=validated.atomic,
        span=validated.span,
        verdict=_parse_verdict(validated.prediction),
        influences=[
            make_influence(source_id=source_id, text=sentence, span=span)
            for sentence, source_id, span in zip(
                validated.top5_sentences.filtered_sentences,
                validated.top5_sentences.id_pairs,
                validated.top5_sentences.source_spans,
            )
        ],
    )


def _parse_verdict(prediction: PredictionEnum) -> Verdict:
    if prediction == PredictionEnum.supports:
        return Verdict.SUPPORTS
    if prediction == PredictionEnum.refutes:
        return Verdict.REFUTES
    if prediction == PredictionEnum.not_enough_info:
        return Verdict.NOT_ENOUGH_INFO

    # the below is assert_never but in Python 3.10
    def _exhaustive_check(x: NoReturn) -> NoReturn:
        raise Exception(f"Unhandled case: {x}")

    _exhaustive_check(prediction)
