from dataclasses import dataclass
from typing import List, Optional, Tuple

from vajra.datatypes import SamplerOutput  # type: ignore
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import SequenceParams  # type: ignore


@dataclass(frozen=True)
class StepInputs:
    """Input data for a single step of the model.

    Attributes:
        scheduler_output: The outputs from the scheduler for this step.
        new_seq_params: A list of new sequences to add to the engine
        pending_step_outputs: A list of tuples of scheduler outputs and sampler outputs
    """

    scheduler_output: SchedulerOutput
    new_seq_params: Optional[List[SequenceParams]] = None
    pending_step_outputs: Optional[
        List[Tuple[SchedulerOutput, List[SamplerOutput]]]
    ] = None


@dataclass(frozen=True)
class StepMicrobatchOutputs:
    schedule_id: int


@dataclass(frozen=True)
class StepOutputs:
    schedule_id: int
    sampler_outputs: List[SamplerOutput]
