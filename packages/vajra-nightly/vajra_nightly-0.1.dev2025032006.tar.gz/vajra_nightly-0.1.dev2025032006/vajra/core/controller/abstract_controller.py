from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from vajra.config import BaseReplicasetControllerConfig, ModelConfig
from vajra.datatypes import RequestOutput, SamplingParams  # type: ignore
from vajra.metrics_store import MetricsStore


class AbstractController(ABC):
    """Abstract base class defining the interface for Vajra controllers.

    This class defines the common interface that all controller implementations
    must adhere to, ensuring consistency across different parallel strategies.

    Note: In the future, we will have an AbstractControllerConfig
    """

    @abstractmethod
    def __init__(
        self,
        config: BaseReplicasetControllerConfig,
        resource_mapping: Optional[Dict[int, List[Tuple[str, int]]]] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        """Initialize the controller with the given configuration.

        Args:
            config: System configuration specifying model, parallel strategy etc.
        """

    @abstractmethod
    def get_model_config(self) -> ModelConfig:
        """Get the model configuration.

        Returns:
            The model configuration used by this controller.
        """

    @abstractmethod
    def add_request(
        self,
        prompt: str,
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
    ) -> None:
        """Add a request to be processed by the controller.

        Args:
            prompt: The input text prompt
            sampling_params: Parameters controlling text generation
            prompt_token_ids: Optional pre-tokenized prompt
            seq_id: Optional unique identifier for the request
        """

    @abstractmethod
    def step(self, block: bool = False) -> List[RequestOutput]:
        """Perform one step of processing and return any available outputs.

        Args:
            block: Whether to block until outputs are available

        Returns:
            List of RequestOutput objects containing generated text and metadata
        """

    @abstractmethod
    def get_metric_store(self) -> MetricsStore:
        """Get the metrics store for this controller.

        Returns:
            The metrics store containing performance metrics.
        """

    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset all metrics collection."""

    @abstractmethod
    def pull_worker_metrics(self) -> None:
        """Pull metrics from all workers."""

    @abstractmethod
    def plot_metrics(self) -> None:
        """Plot collected metrics."""
