from queue import PriorityQueue
from typing import Any, Dict

from vajra.core.scheduler.replicaset_schedulers import BaseReplicasetScheduler
from vajra.datatypes import Sequence, SequenceWithPriority
from vajra.logger import init_logger
from vajra.utils.threading_utils import synchronized

logger = init_logger(__name__)


class PullReplicasetScheduler(BaseReplicasetScheduler):
    """Pull-based scheduler where replicas pull work from a global queue."""

    def __init__(self, config: Any, num_replicas: int) -> None:
        super().__init__(config, num_replicas)
        self.replica_queue_mapping: Dict[str, PriorityQueue] = {}
        logger.info(f"PullReplicasetScheduler initialized with {num_replicas} replicas")

    def init_queue(self) -> None:
        # since we are using a single global queue which all replicas pull from, we need to map each replica to the global queue
        self.replica_queue_mapping = {"global": PriorityQueue()}

    def get_replica_queue_mapping(self) -> Dict[str, PriorityQueue]:
        return self.replica_queue_mapping

    def get_replica_queue(self, replica_id: int) -> PriorityQueue:
        return self.replica_queue_mapping["global"]

    @synchronized
    def assign_seq_replica(self, seq: Sequence) -> None:
        wrapped_seq: SequenceWithPriority = SequenceWithPriority(
            seq=seq, priority=(seq.arrival_time, seq.arrival_time)
        )
        # Register with all replicas
        for replica_id in range(self.num_replicas):
            self.replica_controller_mapping[replica_id].on_controller_assignment(seq)
        self.replica_queue_mapping["global"].put(wrapped_seq)

    def get_num_unfinished_requests(self) -> int:
        return self.replica_queue_mapping["global"].qsize()
