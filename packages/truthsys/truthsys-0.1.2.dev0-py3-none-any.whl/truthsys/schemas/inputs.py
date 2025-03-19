from typing import Annotated

from pydantic import BaseModel, Field

from .common import LLMInput, Source


class ReferenceInput(BaseModel):
    start: Annotated[int, Field(ge=0)]
    end: int
    # TODO: change this to uuids
    evidence_ids: list[str]


class OpenAISettings(BaseModel):
    classifier_llm_name: str | None = None
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    metadata: dict[str, str] | None = None
    """Any custom metadata to be passed on with the LLM call, e.g. for tracking purposes."""


class HallucinationDetectionInput(BaseModel):
    # TODO: stronger definitions
    claim: str
    sources: list[Source]
    llm_input: list[LLMInput] | None = None

    openai_settings: OpenAISettings = OpenAISettings()
