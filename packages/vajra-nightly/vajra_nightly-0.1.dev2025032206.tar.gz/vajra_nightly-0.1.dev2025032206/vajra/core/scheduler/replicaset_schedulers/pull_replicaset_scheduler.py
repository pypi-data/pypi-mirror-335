from queue import PriorityQueue

from vajra.config import PullReplicasetSchedulerConfig
from vajra.core.scheduler.replicaset_schedulers import BaseReplicasetScheduler
from vajra.datatypes import BaseSequenceWithPriority
from vajra.logger import init_logger

logger = init_logger(__name__)


class PullReplicasetScheduler(BaseReplicasetScheduler):
    """Pull-based scheduler where replicas pull work from a global queue."""

    def __init__(
        self, config: PullReplicasetSchedulerConfig, num_replicas: int
    ) -> None:
        super().__init__(config, num_replicas)
        self.replica_queue_mapping: PriorityQueue = PriorityQueue()

    def get_replica_queue(self, replica_id: int) -> PriorityQueue:
        return self.replica_queue_mapping

    def schedule(self, seq: BaseSequenceWithPriority) -> None:
        self.replica_queue_mapping.put(seq)
