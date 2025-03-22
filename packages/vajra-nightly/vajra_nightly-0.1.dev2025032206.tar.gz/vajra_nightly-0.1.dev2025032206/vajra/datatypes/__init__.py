from typing import Dict, List, Tuple

from vajra._native.datatypes import (
    BaseSequenceWithPriority,
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
    UserSequenceParams,
)

from .comm_info import CommInfo
from .tokenizer_protocol import TokenizerInput, TokenizerOutput
from .zmq_protocol import StepInputs, StepMicrobatchOutputs, StepOutputs

GPULocation = Tuple[str, int]  # (node_ip, gpu_id)
ResourceMapping = List[GPULocation]
GlobalResourceMapping = Dict[int, ResourceMapping]

SamplerOutputs = List[SamplerOutput]
ModelParallelRank = Tuple[int, int, int]


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
    "BaseSequenceWithPriority",
    "StepInputs",
    "StepMicrobatchOutputs",
    "StepOutputs",
    "SamplingType",
    "TokenizerInput",
    "TokenizerOutput",
    "GPULocation",
    "ResourceMapping",
    "GlobalResourceMapping",
    "SequenceMetadata",
    "SequenceParams",
    "UserSequenceParams",
    "ModelParallelRank",
]
