from dataclasses import dataclass
from typing import List

from vajra.datatypes import SamplingParams  # type: ignore


@dataclass(frozen=True)
class TokenizerInput:
    seq_id: str
    arrival_time: float
    prompt: str
    sampling_params: SamplingParams


@dataclass(frozen=True)
class TokenizerOutput:
    seq_id: str
    arrival_time: float
    prompt: str
    prompt_token_ids: List[int]
    sampling_params: SamplingParams
