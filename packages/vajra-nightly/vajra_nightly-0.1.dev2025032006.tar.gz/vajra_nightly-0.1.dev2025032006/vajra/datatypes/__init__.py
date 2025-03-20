from typing import List, Optional, Tuple

from vajra._native.datatypes import (
    LogicalTokenBlock,
    RequestOutput,
    SamplerOutput,
    SamplingParams,
    SamplingType,
    SchedulerOutput,
    Sequence,
    SequenceMetadata,
    SequenceParams,
    SequenceScheduleMetadata,
    SequenceState,
    SequenceStatus,
    SequenceWithPriority,
)

from .comm_info import CommInfo
from .tokenizer_protocol import TokenizerInput, TokenizerOutput
from .zmq_protocol import StepInputs, StepMicrobatchOutputs, StepOutputs

GPULocation = Tuple[Optional[str], int]  # (node_ip, gpu_id)
ResourceMapping = List[GPULocation]

SamplerOutputs = List[SamplerOutput]


__all__ = [
    "LogicalTokenBlock",
    "CommInfo",
    "RequestOutput",
    "SamplerOutput",
    "SamplerOutputs",
    "SamplingParams",
    "SchedulerOutput",
    "SequenceScheduleMetadata",
    "SequenceState",
    "SequenceStatus",
    "Sequence",
    "SequenceWithPriority",
    "StepInputs",
    "StepMicrobatchOutputs",
    "StepOutputs",
    "SamplingType",
    "TokenizerInput",
    "TokenizerOutput",
    "GPULocation",
    "ResourceMapping",
    "SequenceMetadata",
    "SequenceParams",
]
