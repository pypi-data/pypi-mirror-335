from abc import ABC, abstractmethod
from queue import Queue

from vajra.config import ModelConfig
from vajra.datatypes import GlobalResourceMapping
from vajra.metrics_store import EngineMetricsStore


class AbstractController(ABC):
    """Abstract base class defining the interface for Vajra controllers.

    This class defines the common interface that all controller implementations
    must adhere to, ensuring consistency across different parallel strategies.

    Note: In the future, we will have an AbstractControllerConfig
    """

    @abstractmethod
    def __init__(
        self,
        global_resource_mapping: GlobalResourceMapping,
        waiting_seq_queue: Queue,
        output_queue: Queue,
    ) -> None:
        """Initialize the controller with the given configuration.

        Args:
            config: System configuration specifying model, parallel strategy etc.
            global_resource_mapping: Mapping of resources to replicas
            waiting_seq_queue: Queue to which waiting sequences are sent
            output_queue: Queue to which outputs are sent
        """
        self.global_resource_mapping = global_resource_mapping
        self.waiting_seq_queue = waiting_seq_queue
        self.output_queue = output_queue

    @abstractmethod
    def get_metric_store(self) -> EngineMetricsStore:
        """Get the metrics store for this controller.

        Returns:
            The metrics store containing performance metrics.
        """

    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset all metrics collection."""

    @abstractmethod
    def get_model_config(self) -> ModelConfig:
        """Get the model configuration.

        Returns:
            The model configuration used by this controller.
        """
