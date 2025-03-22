import time
from queue import Empty, Queue
from typing import List, Optional

from vajra.config import InferenceEngineConfig, ModelConfig
from vajra.core.controller.replicaset_controllers.replicaset_controller_registry import (
    ReplicasetControllerRegistry,
)
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.datatypes import UserSequenceParams  # type: ignore
from vajra.engine.resource_allocator import ResourceAllocator
from vajra.enums import MetricsStoreType  # type: ignore
from vajra.logger import init_logger
from vajra.metrics_store import EngineMetricsStore, MetricsStoreHandle
from vajra.utils import Counter
from vajra.utils.logging_utils import print_resource_mapping, print_vajra_banner

logger = init_logger(__name__)


class InferenceEngine:
    """High-level inference engine for Vajra.

    This is the main entry point for using Vajra. It provides a simple interface
    for adding requests and getting outputs from the underlying controller.

    Args:
        config: Engine configuration specifying model, parallel strategy etc.
    """

    def __init__(self, config: InferenceEngineConfig) -> None:
        """Initialize the inference engine with resource allocation"""
        # Handle resource allocation at the engine level
        resource_mapping = config.global_resource_mapping
        if resource_mapping is None:
            resource_allocator = ResourceAllocator()
            resource_mapping = resource_allocator.get_replicaset_resource_mapping(
                config.controller_config.num_replicas,
                config.controller_config.replica_controller_config.parallel_config.world_size,
            )

        print_vajra_banner()
        print_resource_mapping(resource_mapping)

        metrics_store = MetricsStoreHandle.get_or_create_instance(
            MetricsStoreType.ENGINE,
            config.metrics_config,
        )
        assert isinstance(metrics_store, EngineMetricsStore)
        self.metrics_store = metrics_store

        self.waiting_seq_queue: Queue[UserSequenceParams] = Queue()
        self.output_queue: Queue[RequestOutput] = Queue()

        self.seq_counter = Counter()
        self.controller = ReplicasetControllerRegistry.get(
            config.controller_config.get_type(),
            config.controller_config,
            resource_mapping,
            self.waiting_seq_queue,
            self.output_queue,
        )

    def add_request(
        self,
        prompt: str,
        sampling_params: SamplingParams,
        prompt_token_ids: List[int] = [],
        seq_id: Optional[str] = None,
    ) -> None:
        """Add a request to be processed.

        Args:
            prompt: The input text prompt
            sampling_params: Parameters controlling text generation
            prompt_token_ids: Optional pre-tokenized prompt
            seq_id: Optional unique identifier for the request
        """
        if seq_id is None:
            seq_id = str(next(self.seq_counter))

        arrival_time = time.time()

        self.waiting_seq_queue.put(
            UserSequenceParams(
                seq_id,
                prompt,
                prompt_token_ids,
                arrival_time,
                sampling_params,
            )
        )

        self.metrics_store.on_request_arrival(seq_id, arrival_time)

    def get_outputs(self, block: bool = False) -> List[RequestOutput]:
        """Get any available outputs from processed requests.

        Returns:
            List of RequestOutput objects containing generated text and metadata
        """
        try:
            return self.output_queue.get(block=block)
        except Empty:
            return []

    def abort(self, seq_id: str) -> None:
        """Abort a specific request.

        Args:
            seq_id: The unique identifier of the request to abort
        """
        # TODO: Implement abort functionality in controllers
        raise NotImplementedError("Abort functionality not yet implemented")

    def reset_metrics(self) -> None:
        """Reset all metrics collection."""
        self.controller.reset_metrics()

    def plot_metrics(self) -> None:
        """Plot collected metrics."""
        self.controller.get_metric_store().plot()

    def get_model_config(self) -> ModelConfig:
        """Return the model configuration for this replica set."""
        return self.controller.get_model_config()
