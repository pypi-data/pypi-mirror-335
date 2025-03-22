from queue import PriorityQueue, Queue

from vajra.config import BaseReplicaControllerConfig, ModelConfig
from vajra.core.controller.abstract_controller import AbstractController
from vajra.core.scheduler.request_prioritizers.base_request_prioritizer import (
    BaseRequestPrioritizer,
)
from vajra.datatypes import BaseSequenceWithPriority  # type: ignore
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import (
    ResourceMapping,
)
from vajra.logger import init_logger

logger = init_logger(__name__)


class BaseReplicaController(AbstractController):
    """Base controller class that implements common functionality for all replica controllers.

    This class provides the foundation for different types of replica controllers,
    implementing common functionality and defining the interface that all replica
    controllers must implement.

    Args:
        config: System Config: The system configuration for the engine.
    """

    def __init__(
        self,
        replica_id: int,
        config: BaseReplicaControllerConfig,
        resource_mapping: ResourceMapping,
        request_prioritizer: BaseRequestPrioritizer,
        waiting_seq_queue: PriorityQueue[BaseSequenceWithPriority],
        output_queue: Queue[RequestOutput],
    ) -> None:
        self.config = config
        self.replica_id = replica_id
        self.output_queue = output_queue
        self.waiting_seq_queue = waiting_seq_queue
        self.resource_mapping = resource_mapping
        self.request_prioritizer = request_prioritizer

    def get_model_config(self) -> ModelConfig:
        """Get the model configuration."""
        return self.config.model_config
