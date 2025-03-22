from vajra._native.core.scheduler.replica_schedulers.trackers import (
    BatchFormationTrackerWithRuntimePrediction,
)
from vajra.config.replica_scheduler_config import SpaceSharingReplicaSchedulerConfig
from vajra.core.scheduler.replica_schedulers.dynamic_chunk_replica_scheduler import (
    DynamicChunkReplicaScheduler,
)
from vajra.core.scheduler.request_prioritizers.lrs_request_prioritizer import (
    LrsRequestPrioritizer,
)
from vajra.datatypes import Sequence

MAX_SPACE_SHARE_FRAC = 0.5


class SpaceSharingReplicaScheduler(DynamicChunkReplicaScheduler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert isinstance(
            self.request_prioritizer, LrsRequestPrioritizer
        ), "Space sharing replica scheduler can only be used with LRS request prioritizer"

    def _get_seq_next_num_q_tokens(
        self,
        seq: Sequence,
        batch_formation_tracker: BatchFormationTrackerWithRuntimePrediction,
    ) -> int:
        assert isinstance(self.scheduler_config, SpaceSharingReplicaSchedulerConfig)
        assert not seq.is_finished()
        assert not seq.prompt_stage_processing_finished

        active_kvp_group_ids = self.kvp_state_tracker.get_active_kvp_group_ids(seq)
        num_processed_tokens = seq.get_num_prompt_tokens_stage_processed()

        if num_processed_tokens < self.scheduler_config.long_seq_kv_cache_len_threshold:
            target_time = self.scheduler_config.target_batch_time
        else:
            # avoid space sharing with another long seq
            if any(
                any(
                    x > self.scheduler_config.long_seq_kv_cache_len_threshold
                    for x in batch_formation_tracker.per_kvp_group_seq_num_processed_tokens[
                        kvp_group_id
                    ]
                )
                for kvp_group_id in active_kvp_group_ids
            ):
                return 0

            # NOTE: Space sharing is scheduler can starve long requests,
            # so we use the slack computed in the lrs request prioritizer
            # to compute the target time -- this we can run space sharing
            # replica scheduler only with lrs request prioritizer
            # TODO(Amey): We should identify a better way to compute the slack
            slack_fraction = self.request_prioritizer.get_seq_with_priority(
                seq
            ).get_priority()
            slack_fraction = max(0.0, slack_fraction)
            slack_fraction = min(MAX_SPACE_SHARE_FRAC, slack_fraction)
            target_time = self.scheduler_config.target_batch_time * (1 - slack_fraction)

        # Cast to the derived class to access runtime prediction methods
        runtime_tracker = batch_formation_tracker
        assert isinstance(runtime_tracker, BatchFormationTrackerWithRuntimePrediction)
        next_num_tokens = runtime_tracker.get_max_chunk_size_for_seq(
            seq,
            active_kvp_group_ids,
            target_time,
        )

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
