from queue import PriorityQueue
from typing import Dict

from vajra.config import RoundRobinReplicasetSchedulerConfig
from vajra.core.scheduler.replicaset_schedulers import BaseReplicasetScheduler
from vajra.datatypes import BaseSequenceWithPriority
from vajra.logger import init_logger
from vajra.utils.threading_utils import synchronized

logger = init_logger(__name__)


class RoundRobinReplicasetScheduler(BaseReplicasetScheduler):
    """Round-robin scheduler that distributes requests across replicas."""

    def __init__(
        self, config: RoundRobinReplicasetSchedulerConfig, num_replicas: int
    ) -> None:
        super().__init__(config, num_replicas)
        self.current_replica_id: int = 0
        self.replica_queue_mapping: Dict[int, PriorityQueue] = {
            replica_id: PriorityQueue() for replica_id in range(self.num_replicas)
        }

    def get_replica_queue(self, replica_id: int) -> PriorityQueue:
        return self.replica_queue_mapping[replica_id]

    @synchronized
    def schedule(self, seq: BaseSequenceWithPriority) -> None:
        replica_id = self.current_replica_id
        self.replica_queue_mapping[replica_id].put(seq)
        self.current_replica_id = (self.current_replica_id + 1) % self.num_replicas
