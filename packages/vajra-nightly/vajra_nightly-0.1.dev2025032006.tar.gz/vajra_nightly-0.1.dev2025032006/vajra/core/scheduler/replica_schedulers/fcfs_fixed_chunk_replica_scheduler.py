from typing import Any

from vajra._native.scheduler import BatchFormationTracker
from vajra.core.scheduler.replica_schedulers.base_replica_scheduler import (
    BaseReplicaScheduler,
)
from vajra.datatypes import Sequence  # type: ignore


class FcfsFixedChunkReplicaScheduler(BaseReplicaScheduler):
    def _get_seq_next_num_q_tokens(
        self, seq: Sequence, batch_formation_tracker: BatchFormationTracker
    ) -> int:
        assert not seq.is_finished()
        assert not seq.prompt_stage_processing_finished

        batched_num_q_tokens_across_groups = (
            self.kvp_state_tracker.get_batch_tracker_q_tokens(seq)
        )
        max_num_q_tokens_across_groups = max(batched_num_q_tokens_across_groups)

        num_processed_tokens = seq.get_num_prompt_tokens_stage_processed()

        next_num_tokens = min(
            seq.prompt_len - num_processed_tokens,
            self.scheduler_config.chunk_size - max_num_q_tokens_across_groups,
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

    def _get_seq_priority(self, seq: Sequence) -> Any:
        return (seq.arrival_time, seq.arrival_time)
