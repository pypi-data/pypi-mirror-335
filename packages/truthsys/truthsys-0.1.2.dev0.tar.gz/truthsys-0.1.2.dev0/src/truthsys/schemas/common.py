from typing import List, NamedTuple, Tuple

from pydantic import BaseModel


class Top5Sentences(NamedTuple):
    filtered_sentences: List[str]
    id_pairs: List[str]
    scores: List[List[float]]
    source_spans: List[Tuple[int, int]]


class Source(BaseModel):
    id: str
    text: str
    score: float | None = None


class LLMInput(BaseModel):
    role: str
    content: str
