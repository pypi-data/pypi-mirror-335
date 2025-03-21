from typing import Any

from vidur.config import RandomForrestExecutionTimePredictorConfig
from vidur.config import ReplicaConfig as VidurReplicaConfig
from vidur.execution_time_predictor import ExecutionTimePredictorRegistry

from vajra._native.scheduler import (
    BatchFormationTracker,
    BatchFormationTrackerWithRuntimePrediction,
)
from vajra.core.scheduler.replica_schedulers.base_replica_scheduler import (
    BaseReplicaScheduler,
)
from vajra.datatypes import Sequence  # type: ignore

PREDICTION_MAX_CHUNK_SIZE = 4 * 1024
MAX_TOKENS_PER_SEQ = 2 * 1024 * 1024
PREDICTION_MAX_BATCH_SIZE = 128
PREDICTION_DEVICE = "h100"
PREDICTION_NETWORK_DEVICE = "h100_dgx"
# PREDICTION_DEVICE = "a100"
# PREDICTION_NETWORK_DEVICE = "a100_dgx"
KV_CACHE_PREDICTION_GRANULARITY = 512
MODEL_NAME_MAPPING = {
    "meta-llama/Meta-Llama-3-8B": "meta-llama/Llama-3-8B",
    "meta-llama/Meta-Llama-3-8B-Instruct": "meta-llama/Llama-3-8B",
    "gradientai/Llama-3-8B-Instruct-Gradient-1048k": "meta-llama/Llama-3-8B",
    "gradientai/Llama-3-70B-Instruct-Gradient-1048k": "meta-llama/Llama-2-70b-hf",
}

EXECUTION_TIME_PREDICTION_SLACK = 0.1
EXECUTION_TIME_PREDICTION_START_CHUNK_SIZE = 512
EXECUTION_TIME_PREDICTION_CHUNK_SIZE_GRANULARITY = 32


def round_down_to_nearest_multiple(value: int, multiple: int) -> int:
    return (value // multiple) * multiple


def round_up_to_nearest_multiple(value: int, multiple: int) -> int:
    return ((value + multiple - 1) // multiple) * multiple


class FcfsReplicaScheduler(BaseReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        execution_time_predictor_config = RandomForrestExecutionTimePredictorConfig(
            prediction_max_prefill_chunk_size=PREDICTION_MAX_CHUNK_SIZE,
            prediction_max_tokens_per_request=MAX_TOKENS_PER_SEQ,
            prediction_max_batch_size=PREDICTION_MAX_BATCH_SIZE,
            kv_cache_prediction_granularity=KV_CACHE_PREDICTION_GRANULARITY,
            use_native_execution_time_predictor=True,  # Explicitly enable native predictor
        )
        vidur_replica_config = VidurReplicaConfig(
            model_name=MODEL_NAME_MAPPING[self.model_config.model],
            num_pipeline_stages=self.parallel_config.pipeline_parallel_size,
            tensor_parallel_size=self.parallel_config.tensor_parallel_size,
            kv_parallel_size=self.parallel_config.kv_parallel_size,
            max_num_tokens_per_kvp_group=self.parallel_config.max_num_tokens_per_kvp_group,
            enable_sequence_pipeline_parallel=self.parallel_config.enable_sequence_pipeline_parallel,
            device=PREDICTION_DEVICE,
            network_device=PREDICTION_NETWORK_DEVICE,
            block_size=self.cache_config.block_size,
        )
        self.execution_time_predictor = ExecutionTimePredictorRegistry.get(
            execution_time_predictor_config.get_type(),
            predictor_config=execution_time_predictor_config,
            replica_config=vidur_replica_config,
        )

        # Make sure the native_execution_time_predictor is initialized
        if not self.execution_time_predictor._native_execution_time_predictor:
            raise ValueError(
                "execution_time_predictor does not have _native_execution_time_predictor attribute"
            )

        # Get a direct reference to the native C++ predictor
        self.native_execution_time_predictor = (
            self.execution_time_predictor._native_execution_time_predictor
        )

    def _get_batch_formation_tracker(self) -> BatchFormationTracker:
        # Pass the native predictor directly - it's a pybind11 object that can be cast directly
        return BatchFormationTrackerWithRuntimePrediction(
            schedule_id=self._iteration_id,
            max_micro_batch_size=self.scheduler_config.max_batch_size,
            pipeline_parallel_size=self.parallel_config.pipeline_parallel_size,
            kvp_state_tracker=self.kvp_state_tracker,
            max_chunk_size=self.scheduler_config.max_chunk_size,
            min_chunk_size=self.scheduler_config.min_chunk_size,
            execution_time_predictor_capsule=self.native_execution_time_predictor.as_capsule(),
        )

    def _get_seq_next_num_q_tokens(
        self, seq: Sequence, batch_formation_tracker: BatchFormationTracker
    ) -> int:
        assert not seq.is_finished()
        assert not seq.prompt_stage_processing_finished

        active_kvp_group_ids = self.kvp_state_tracker.get_active_kvp_group_ids(seq)

        # Cast to the derived class to access runtime prediction methods
        runtime_tracker = batch_formation_tracker
        assert isinstance(runtime_tracker, BatchFormationTrackerWithRuntimePrediction)
        next_num_tokens = runtime_tracker.get_max_chunk_size_for_seq(
            seq,
            active_kvp_group_ids,
            self.scheduler_config.target_batch_time,
        )

        num_processed_tokens = seq.get_num_tokens_stage_processed()
        if self.parallel_config.kv_parallel_size > 1:
            last_group_tokens = (
                num_processed_tokens
                % self.kvp_state_tracker.get_max_num_tokens_per_kvp_group()
            )
            next_num_tokens = min(
                next_num_tokens,
                self.kvp_state_tracker.get_max_num_tokens_per_kvp_group()
                - last_group_tokens,
            )

        next_num_tokens = max(0, next_num_tokens)

        return next_num_tokens

    def _get_seq_priority(self, seq: Sequence) -> Any:
        return (seq.arrival_time, seq.arrival_time)
