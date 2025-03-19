import time

from vajra.core.scheduler.replica_schedulers.edf_replica_scheduler import (
    EdfReplicaScheduler,
)
from vajra.datatypes import Sequence  # type: ignore


class LrsReplicaScheduler(EdfReplicaScheduler):

    def _get_remaining_slack_fraction(
        self, current_time: float, seq: Sequence
    ) -> float:
        remaining_prefill_time = self._prefill_time_calculator.get_prefill_time(
            seq.prompt_len,
            seq.get_num_prompt_tokens_stage_processed(),
        )
        slack = seq.deadline - current_time - remaining_prefill_time
        return slack / seq.deadline_time

    def _sort_waiting_queue(self) -> None:
        current_time = time.time()

        self.waiting.sort(
            key=lambda x: self._get_remaining_slack_fraction(current_time, x[1])
        )
