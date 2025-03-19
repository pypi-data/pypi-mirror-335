from queue import PriorityQueue
from typing import Any, Dict

from vajra.core.scheduler.replicaset_schedulers import BaseReplicasetScheduler
from vajra.datatypes import Sequence, SequenceWithPriority
from vajra.logger import init_logger
from vajra.utils.threading_utils import synchronized

logger = init_logger(__name__)


class RoundRobinReplicasetScheduler(BaseReplicasetScheduler):
    """Round-robin scheduler that distributes requests across replicas."""

    def __init__(self, config: Any, num_replicas: int) -> None:
        super().__init__(config, num_replicas)
        self.current_replica_id: int = 0
        self.replica_queue_mapping: Dict[int, PriorityQueue] = {}
        logger.info(
            f"RoundRobinReplicasetScheduler initialized with {num_replicas} replicas"
        )

    def init_queue(self) -> None:
        self.replica_queue_mapping = {
            replica_id: PriorityQueue() for replica_id in range(self.num_replicas)
        }

    def get_replica_queue_mapping(self) -> Dict[int, PriorityQueue]:
        return self.replica_queue_mapping

    def get_replica_queue(self, replica_id: int) -> PriorityQueue:
        return self.replica_queue_mapping[replica_id]

    @synchronized
    def assign_seq_replica(self, seq: Sequence) -> None:
        replica_id = self.current_replica_id
        wrapped_seq: SequenceWithPriority = SequenceWithPriority(
            seq=seq, priority=(seq.arrival_time, seq.arrival_time)
        )
        self.replica_queue_mapping[replica_id].put(wrapped_seq)
        self.replica_controller_mapping[replica_id].on_controller_assignment(seq)
        self.current_replica_id = (self.current_replica_id + 1) % self.num_replicas

    def get_num_unfinished_requests(self) -> int:
        return sum(q.qsize() for q in self.replica_queue_mapping.values())
