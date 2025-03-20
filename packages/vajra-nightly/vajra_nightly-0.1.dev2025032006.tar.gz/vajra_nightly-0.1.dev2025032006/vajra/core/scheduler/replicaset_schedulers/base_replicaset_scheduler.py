from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Any, Dict, Mapping, TypeVar

from vajra.core.controller.abstract_controller import AbstractController
from vajra.datatypes import Sequence
from vajra.logger import init_logger
from vajra.utils.threading_utils import synchronized

logger = init_logger(__name__)

# Type variable for queue keys
QueueKey = TypeVar("QueueKey")


class BaseReplicasetScheduler(ABC):
    """Base scheduler for managing a set of replicas.

    This abstract class defines the interface for replica set schedulers.
    Implementations must provide concrete logic for queue management and
    sequence assignment strategies.

    Args:
        config: Configuration object for the scheduler
        num_replicas: Number of replicas to manage
    """

    def __init__(self, config: Any, num_replicas: int) -> None:
        self.config = config
        self.num_replicas = num_replicas
        self.replica_controller_mapping: Dict[int, AbstractController] = {}

    @abstractmethod
    def init_queue(self) -> None:
        """Initialize queues for request handling.

        Must be implemented by subclasses to set up their specific queue structure.
        """

    @abstractmethod
    def get_replica_queue(self, replica_id: int) -> PriorityQueue:
        """Get queue for specific replica.

        Args:
            replica_id: ID of the replica

        Returns:
            PriorityQueue associated with the replica
        """

    @abstractmethod
    def get_replica_queue_mapping(self) -> Mapping[QueueKey, PriorityQueue]:
        """Get mapping of all replica queues.

        Returns:
            Mapping from queue keys to PriorityQueues
        """

    def set_replica_controller(
        self, replica_id: int, replica_controller: AbstractController
    ) -> None:
        """Register a replica engine with this scheduler.

        Args:
            replica_id: ID of the replica
            replica_llm_engine: LLM engine instance for the replica
        """
        self.replica_controller_mapping[replica_id] = replica_controller

    @abstractmethod
    @synchronized
    def assign_seq_replica(self, seq: Sequence) -> None:
        """Assign a sequence to replica(s).

        Must be implemented by subclasses to define sequence assignment strategy.

        Args:
            seq: Sequence to be assigned
        """

    @abstractmethod
    def get_num_unfinished_requests(self) -> int:
        """Get total number of unfinished requests.

        Returns:
            Number of requests still in queues
        """

    def has_unfinished_requests(self) -> bool:
        """Check if there are any unfinished requests.

        Returns:
            True if there are unfinished requests, False otherwise
        """
        return self.get_num_unfinished_requests() > 0
