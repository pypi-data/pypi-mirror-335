from abc import abstractmethod
from typing import Any, List, Optional

from vajra.core.controller.abstract_controller import AbstractController
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.metrics_store import MetricsStore


class BaseReplicasetController(AbstractController):
    """Base class for all replica set controllers that manage multiple replicas."""

    @abstractmethod
    def add_request(
        self,
        prompt: Optional[str],
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
        arrival_time: Optional[float] = None,
    ) -> None:
        """Add a new generation request to the controller."""

    @abstractmethod
    def step(self, block: bool = False) -> List[RequestOutput]:
        """Process one step of generation and return outputs."""

    @abstractmethod
    def start_controller_execution(self) -> None:
        """Start all replica controllers (alias for start)."""

    @abstractmethod
    def get_metric_store(self) -> MetricsStore:
        """Get the metrics store for this replica set."""

    @abstractmethod
    def reset_metrics(self) -> None:
        """Reset metrics for all replicas."""

    @abstractmethod
    def start_profiling(self) -> None:
        """Start profiling all replicas."""

    @abstractmethod
    def stop_profiling(self) -> None:
        """Stop profiling all replicas."""

    @abstractmethod
    def pull_worker_metrics(self) -> None:
        """Pull metrics from all replica workers."""

    @abstractmethod
    def has_unfinished_requests(self) -> bool:
        """Check if there are any unfinished requests."""

    @abstractmethod
    def get_num_unfinished_requests(self) -> int:
        """Get number of unfinished requests."""

    @abstractmethod
    def plot_metrics(self) -> None:
        """Plot metrics for this replica set."""

    @abstractmethod
    def get_model_config(self) -> Any:
        """Return the model configuration for this replica set."""
