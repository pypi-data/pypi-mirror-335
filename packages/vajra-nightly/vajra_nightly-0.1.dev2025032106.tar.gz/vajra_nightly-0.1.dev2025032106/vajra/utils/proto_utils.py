"""Protocol Buffer adapters for converting between Python objects and generated protobuf classes"""

from typing import Any, List, Tuple, Type

from vajra.datatypes import SamplerOutput  # type: ignore
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import SequenceParams  # type: ignore
from vajra.datatypes import SequenceScheduleMetadata  # type: ignore
from vajra.datatypes import StepInputs, StepMicrobatchOutputs, StepOutputs
from vajra.datatypes.generated.worker_protocol_pb2 import (
    PendingStepOutput as PendingStepOutputProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    SamplerOutput as SamplerOutputProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    SchedulerOutput as SchedulerOutputProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    SequenceParams as SequenceParamsProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    SequenceScheduleMetadata as SequenceScheduleMetadataProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepInputs as StepInputsProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepMicrobatchOutputs as StepMicrobatchOutputsProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepOutputs as StepOutputsProto,  # type: ignore
)

PendingStepOutput = Tuple[SchedulerOutput, List[SamplerOutput]]


class ProtobufAdapter:
    """Adapter for converting between Python objects and protobuf messages."""

    @staticmethod
    def sampler_output_to_proto(obj: SamplerOutput) -> SamplerOutputProto:  # type: ignore
        """Convert a SamplerOutput to a SamplerOutputProto."""
        proto = SamplerOutputProto()
        proto.schedule_id = obj.schedule_id
        proto.seq_id = obj.seq_id
        proto.output_tokens.extend(obj.output_tokens)
        return proto

    @staticmethod
    def sampler_output_from_proto(proto: SamplerOutputProto) -> SamplerOutput:  # type: ignore
        """Convert a SamplerOutputProto to a SamplerOutput."""
        return SamplerOutput(
            proto.schedule_id,
            proto.seq_id,
            list(proto.output_tokens),
        )

    @staticmethod
    def sequence_params_to_proto(obj: SequenceParams) -> SequenceParamsProto:  # type: ignore
        """Convert a SequenceParams to a SequenceParamsProto."""
        proto = SequenceParamsProto()
        proto.seq_id = obj.seq_id
        proto.prompt = obj.prompt
        proto.prompt_token_ids.extend(obj.prompt_token_ids)
        proto.block_size = obj.block_size
        proto.eos_token_id = obj.eos_token_id
        proto.arrival_time = obj.arrival_time
        proto.sampling_params.temperature = obj.sampling_params.temperature
        proto.sampling_params.top_p = obj.sampling_params.top_p
        proto.sampling_params.top_k = obj.sampling_params.top_k
        proto.sampling_params.ignore_eos = obj.sampling_params.ignore_eos
        proto.sampling_params.max_tokens = obj.sampling_params.max_tokens
        return proto

    @staticmethod
    def sequence_params_from_proto(proto: SequenceParamsProto) -> SequenceParams:  # type: ignore
        """Convert a SequenceParamsProto to a SequenceParams."""
        return SequenceParams(
            proto.seq_id,
            proto.prompt,
            list(proto.prompt_token_ids),
            proto.block_size,
            proto.eos_token_id,
            proto.arrival_time,
            SamplingParams(
                proto.sampling_params.temperature,
                proto.sampling_params.top_p,
                proto.sampling_params.top_k,
                proto.sampling_params.ignore_eos,
                proto.sampling_params.max_tokens,
            ),
        )

    @staticmethod
    def sequence_schedule_metadata_to_proto(
        obj: SequenceScheduleMetadata,
    ) -> SequenceScheduleMetadataProto:  # type: ignore
        """Convert a SequenceScheduleMetadata to a SequenceScheduleMetadataProto."""
        proto = SequenceScheduleMetadataProto()
        proto.schedule_id = obj.schedule_id
        proto.seq_id = obj.seq_id
        proto.num_q_tokens = obj.num_q_tokens
        for kvp_group_id, block_counter in obj.kvp_group_block_counter.items():
            entry = SequenceScheduleMetadataProto.KvpGroupBlockCounterEntry()
            entry.key = kvp_group_id
            entry.value = block_counter
        proto.kvp_group_block_counter.update(obj.kvp_group_block_counter)
        proto.kvp_group_ids.extend(obj.kvp_group_ids)
        proto.is_kvp_request = obj.is_kvp_request
        return proto

    @staticmethod
    def sequence_schedule_metadata_from_proto(
        proto: SequenceScheduleMetadataProto,  # type: ignore
    ) -> SequenceScheduleMetadata:
        """Convert a SequenceScheduleMetadataProto to a SequenceScheduleMetadata."""
        return SequenceScheduleMetadata(
            proto.schedule_id,
            proto.seq_id,
            proto.num_q_tokens,
            {
                kvp_group_id: block_counter
                for kvp_group_id, block_counter in proto.kvp_group_block_counter.items()
            },
            list(proto.kvp_group_ids),
        )

    @staticmethod
    def scheduler_output_to_proto(obj: SchedulerOutput) -> SchedulerOutputProto:  # type: ignore
        """Convert a SchedulerOutput to a SchedulerOutputProto."""
        proto = SchedulerOutputProto()
        proto.schedule_id = obj.id
        proto.ignored_seq_ids.extend(obj.ignored_seq_ids)
        proto.preempted_seq_ids.extend(obj.preempted_seq_ids)
        proto.seq_schedule_metadata_list.extend(
            [
                ProtobufAdapter.sequence_schedule_metadata_to_proto(metadata)
                for metadata in obj.seq_schedule_metadata_list
            ]
        )
        return proto

    @staticmethod
    def pending_step_output_to_proto(obj: PendingStepOutput) -> PendingStepOutputProto:  # type: ignore
        """Convert a PendingStepOutput to a PendingStepOutputProto."""
        proto = PendingStepOutputProto()
        proto.scheduler_output.CopyFrom(
            ProtobufAdapter.scheduler_output_to_proto(obj[0])
        )
        proto.sampler_outputs.extend(
            [ProtobufAdapter.sampler_output_to_proto(output) for output in obj[1]]
        )
        return proto

    @staticmethod
    def pending_step_output_from_proto(proto: PendingStepOutputProto) -> PendingStepOutput:  # type: ignore
        """Convert a PendingStepOutputProto to a PendingStepOutput."""
        return (
            ProtobufAdapter.scheduler_output_from_proto(proto.scheduler_output),
            [
                ProtobufAdapter.sampler_output_from_proto(output)
                for output in proto.sampler_outputs
            ],
        )

    @staticmethod
    def scheduler_output_from_proto(proto: SchedulerOutputProto) -> SchedulerOutput:  # type: ignore
        """Convert a SchedulerOutputProto to a SchedulerOutput."""
        return SchedulerOutput(
            proto.schedule_id,
            list(proto.ignored_seq_ids),
            list(proto.preempted_seq_ids),
            [
                ProtobufAdapter.sequence_schedule_metadata_from_proto(metadata)
                for metadata in proto.seq_schedule_metadata_list
            ],
        )

    @staticmethod
    def step_inputs_to_proto(obj: StepInputs) -> StepInputsProto:  # type: ignore
        """Convert a StepInputs to a StepInputsProto."""
        proto = StepInputsProto()
        if obj.scheduler_output:
            scheduler_output_proto = ProtobufAdapter.scheduler_output_to_proto(
                obj.scheduler_output
            )
            proto.scheduler_output.CopyFrom(scheduler_output_proto)
        if obj.new_seq_params:
            proto.new_seq_params.extend(
                [
                    ProtobufAdapter.sequence_params_to_proto(param)
                    for param in obj.new_seq_params
                ]
            )
        if obj.pending_step_outputs:
            proto.pending_step_outputs.extend(
                [
                    ProtobufAdapter.pending_step_output_to_proto(output)
                    for output in obj.pending_step_outputs
                ]
            )
        return proto

    @staticmethod
    def step_inputs_from_proto(proto: StepInputsProto) -> StepInputs:  # type: ignore
        """Convert a StepInputsProto to a StepInputs."""
        return StepInputs(
            ProtobufAdapter.scheduler_output_from_proto(proto.scheduler_output),
            [
                ProtobufAdapter.sequence_params_from_proto(param)
                for param in proto.new_seq_params
            ],
            [
                ProtobufAdapter.pending_step_output_from_proto(output)
                for output in proto.pending_step_outputs
            ],
        )

    @staticmethod
    def step_outputs_to_proto(obj: StepOutputs) -> StepOutputsProto:  # type: ignore
        """Convert a StepOutputs to a StepOutputsProto."""
        proto = StepOutputsProto()
        proto.schedule_id = obj.schedule_id
        if obj.sampler_outputs:
            proto.sampler_outputs.extend(  # type: ignore
                [
                    ProtobufAdapter.sampler_output_to_proto(output)
                    for output in obj.sampler_outputs
                ]
            )
        return proto

    @staticmethod
    def step_outputs_from_proto(proto: StepOutputsProto) -> StepOutputs:  # type: ignore
        """Convert a StepOutputsProto to a StepOutputs."""
        return StepOutputs(
            proto.schedule_id,
            [
                ProtobufAdapter.sampler_output_from_proto(output)
                for output in proto.sampler_outputs
            ],
        )

    @staticmethod
    def step_microbatch_outputs_to_proto(
        obj: StepMicrobatchOutputs,
    ) -> StepMicrobatchOutputsProto:  # type: ignore
        """Convert a StepMicrobatchOutputs to a StepMicrobatchOutputsProto."""
        proto: StepMicrobatchOutputsProto = StepMicrobatchOutputsProto()  # type: ignore
        proto.schedule_id = obj.schedule_id
        return proto

    @staticmethod
    def step_microbatch_outputs_from_proto(
        proto: StepMicrobatchOutputsProto,  # type: ignore
    ) -> StepMicrobatchOutputs:
        """Convert a StepMicrobatchOutputsProto to a StepMicrobatchOutputs."""
        return StepMicrobatchOutputs(proto.schedule_id)

    @staticmethod
    def to_proto(obj: Any) -> Any:
        """Convert a Python object to a Protocol Buffer message."""
        if isinstance(obj, StepInputs):
            return ProtobufAdapter.step_inputs_to_proto(obj)
        elif isinstance(obj, StepOutputs):
            return ProtobufAdapter.step_outputs_to_proto(obj)
        elif isinstance(obj, StepMicrobatchOutputs):
            return ProtobufAdapter.step_microbatch_outputs_to_proto(obj)
        else:
            raise ValueError(f"Unsupported object type: {type(obj)}")

    @staticmethod
    def from_proto(proto: Any, proto_class: Type[Any]) -> Any:
        """Convert a Protocol Buffer message to a Python object."""
        if proto_class == StepInputsProto:
            step_inputs_proto = StepInputsProto()
            step_inputs_proto.ParseFromString(proto)
            step_inputs = ProtobufAdapter.step_inputs_from_proto(step_inputs_proto)
            return step_inputs
        elif proto_class == StepOutputsProto:
            step_outputs_proto = StepOutputsProto()
            step_outputs_proto.ParseFromString(proto)
            step_outputs = ProtobufAdapter.step_outputs_from_proto(step_outputs_proto)
            return step_outputs
        elif proto_class == StepMicrobatchOutputsProto:
            step_microbatch_outputs_proto = StepMicrobatchOutputsProto()
            step_microbatch_outputs_proto.ParseFromString(proto)
            step_microbatch_outputs = (
                ProtobufAdapter.step_microbatch_outputs_from_proto(
                    step_microbatch_outputs_proto
                )
            )
            return step_microbatch_outputs
        else:
            raise ValueError(f"Unsupported Protocol Buffer message type: {proto_class}")
