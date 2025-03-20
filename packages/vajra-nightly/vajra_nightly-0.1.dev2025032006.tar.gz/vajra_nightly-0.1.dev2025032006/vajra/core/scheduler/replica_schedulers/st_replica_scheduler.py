import time

from vajra._native.scheduler import BatchFormationTracker
from vajra.core.scheduler.replica_schedulers.lrs_replica_scheduler import (
    LrsReplicaScheduler,
)
from vajra.datatypes import Sequence  # type: ignore

MAX_SPACE_SHARE_FRAC = 0.5


class StReplicaScheduler(LrsReplicaScheduler):

    def _get_seq_next_num_q_tokens(
        self, seq: Sequence, batch_formation_tracker: BatchFormationTracker
    ) -> int:
        assert not seq.is_finished()
        assert not seq.prompt_stage_processing_finished

        active_kvp_group_ids = self._get_active_kvp_group_ids(seq)
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

            slack_fraction = self._get_remaining_slack_fraction(time.time(), seq)
            slack_fraction = max(0.0, slack_fraction)
            slack_fraction = min(MAX_SPACE_SHARE_FRAC, slack_fraction)
            target_time = self.scheduler_config.target_batch_time * (1 - slack_fraction)

        next_num_tokens = batch_formation_tracker.get_max_chunk_size_for_seq(
            seq,
            active_kvp_group_ids,
            target_time,
        )

        if self.parallel_config.kv_parallel_size > 1:
            last_group_tokens = num_processed_tokens % self.max_num_tokens_per_kvp_group
            next_num_tokens = min(
                next_num_tokens,
                self.max_num_tokens_per_kvp_group - last_group_tokens,
            )

        next_num_tokens = max(0, next_num_tokens)

        return next_num_tokens
