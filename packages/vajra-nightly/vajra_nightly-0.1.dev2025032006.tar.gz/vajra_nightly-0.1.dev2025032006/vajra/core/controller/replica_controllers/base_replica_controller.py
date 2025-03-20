from typing import Any, List, Optional, Tuple

from vajra.config import LlmReplicaControllerConfig, ModelConfig
from vajra.core.controller.abstract_controller import AbstractController
from vajra.datatypes import RequestOutput, SamplingParams, Sequence  # type: ignore
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
        config: LlmReplicaControllerConfig,
        resources: Optional[List[Tuple[str, int]]] = None,
        output_dir: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        self.config = config
        self.output_dir = output_dir
        self.replica_id = replica_id
        self.resources = resources

    def get_model_config(self) -> ModelConfig:
        """Get the model configuration."""
        return self.config.model_config

    def add_request(
        self,
        prompt: str,
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
    ) -> None:
        """Add a request to the controller.

        Args:
            prompt: The prompt text
            sampling_params: Parameters for sampling
            prompt_token_ids: Optional pre-tokenized prompt
            seq_id: Optional sequence ID
        """
        raise NotImplementedError("add_request must be implemented by subclasses")

    def get_num_unfinished_requests(self) -> int:
        """Get the number of unfinished requests."""
        raise NotImplementedError(
            "get_num_unfinished_requests must be implemented by subclasses"
        )

    def has_unfinished_requests(self) -> bool:
        """Check if there are any unfinished requests."""
        raise NotImplementedError(
            "has_unfinished_requests must be implemented by subclasses"
        )

    def step(self, block: bool = False) -> List[RequestOutput]:
        """Perform one step of processing.

        Args:
            block: Whether to block until results are available

        Returns:
            List of request outputs
        """
        raise NotImplementedError("step must be implemented by subclasses")

    def on_controller_assignment(self, seq: Sequence) -> None:
        """Handle a sequence being assigned to this controller.

        Args:
            seq: The assigned sequence
        """
        raise NotImplementedError(
            "on_controller_assignment must be implemented by subclasses"
        )

    def start_controller_execution(self) -> None:
        """Start the controller execution loop."""
        raise NotImplementedError(
            "start_controller_execution must be implemented by subclasses"
        )

    def plot_metrics(self) -> None:
        """Plot controller metrics."""
        raise NotImplementedError("plot_metrics must be implemented by subclasses")

    def pull_worker_metrics(self) -> None:
        """Pull metrics from workers."""
        raise NotImplementedError(
            "pull_worker_metrics must be implemented by subclasses"
        )

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        raise NotImplementedError("reset_metrics must be implemented by subclasses")

    def start_profiling(self) -> None:
        """Start profiling."""
        raise NotImplementedError("start_profiling must be implemented by subclasses")

    def stop_profiling(self) -> None:
        """Stop profiling."""
        raise NotImplementedError("stop_profiling must be implemented by subclasses")

    def get_metric_store(self) -> Any:
        """Get the metrics store.

        Returns:
            The metrics store
        """
        raise NotImplementedError("get_metric_store must be implemented by subclasses")
