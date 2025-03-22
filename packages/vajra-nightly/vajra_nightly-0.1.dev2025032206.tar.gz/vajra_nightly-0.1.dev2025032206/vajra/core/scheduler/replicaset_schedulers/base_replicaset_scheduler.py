from abc import ABC, abstractmethod
from queue import PriorityQueue

from vajra.config import BaseReplicasetSchedulerConfig
from vajra.datatypes import BaseSequenceWithPriority


class BaseReplicasetScheduler(ABC):
    """Base scheduler for managing a set of replicas.

    This abstract class defines the interface for replica set schedulers.
    Implementations must provide concrete logic for queue management and
    sequence assignment strategies.

    Args:
        config: Configuration object for the scheduler
        num_replicas: Number of replicas to manage
    """

    def __init__(
        self, config: BaseReplicasetSchedulerConfig, num_replicas: int
    ) -> None:
        self.config = config
        self.num_replicas = num_replicas

    @abstractmethod
    def get_replica_queue(self, replica_id: int) -> PriorityQueue:
        """Get queue for specific replica.

        Args:
            replica_id: ID of the replica

        Returns:
            PriorityQueue associated with the replica
        """

    @abstractmethod
    def schedule(self, seq: BaseSequenceWithPriority) -> None:
        """Assign a sequence to replica(s).

        Must be implemented by subclasses to define sequence assignment strategy.

        Args:
            seq: Sequence to be assigned
        """
