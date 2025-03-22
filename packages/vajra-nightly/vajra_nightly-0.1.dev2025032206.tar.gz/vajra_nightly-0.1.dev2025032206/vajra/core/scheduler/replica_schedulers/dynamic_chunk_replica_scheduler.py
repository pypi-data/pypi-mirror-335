from vajra._native.core.scheduler.replica_schedulers.trackers import (
    BatchFormationTrackerWithRuntimePrediction,
)
from vajra.config import DynamicChunkReplicaSchedulerConfig
from vajra.core.scheduler.replica_schedulers.base_replica_scheduler import (
    BaseReplicaScheduler,
)
from vajra.core.scheduler.utils.execution_time_predictor_factory import (
    ExecutionTimePredictorFactory,
)
from vajra.datatypes import Sequence


class DynamicChunkReplicaScheduler(BaseReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use the factory to get the execution time predictor and its native implementation
        self.execution_time_predictor = (
            ExecutionTimePredictorFactory.get_execution_time_predictor(
                model_config=self.model_config,
                parallel_config=self.parallel_config,
                cache_config=self.cache_config,
            )
        )

    def _get_batch_formation_tracker(
        self,
    ) -> BatchFormationTrackerWithRuntimePrediction:
        assert isinstance(self.scheduler_config, DynamicChunkReplicaSchedulerConfig)

        execution_time_predictor_capsule = (
            self.execution_time_predictor._native_execution_time_predictor.as_capsule()
        )

        return BatchFormationTrackerWithRuntimePrediction(
            schedule_id=self._iteration_id,
            max_micro_batch_size=self.scheduler_config.max_batch_size,
            pipeline_parallel_size=self.parallel_config.pipeline_parallel_size,
            kvp_state_tracker=self.kvp_state_tracker,
            max_chunk_size=self.scheduler_config.max_chunk_size,
            min_chunk_size=self.scheduler_config.min_chunk_size,
            execution_time_predictor_capsule=execution_time_predictor_capsule,
        )

    def _get_seq_next_num_q_tokens(
        self,
        seq: Sequence,
        batch_formation_tracker: BatchFormationTrackerWithRuntimePrediction,
    ) -> int:
        assert not seq.is_finished()
        assert not seq.prompt_stage_processing_finished
        assert isinstance(self.scheduler_config, DynamicChunkReplicaSchedulerConfig)

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
