from typing import List, Optional

from vajra.config import InferenceEngineConfig
from vajra.core.controller.controller_factory import ControllerFactory
from vajra.datatypes import RequestOutput, SamplingParams  # type: ignore
from vajra.engine.resource_allocator import ResourceAllocator
from vajra.logger import init_logger
from vajra.utils.logging_utils import pretty_print_resource_mapping, print_vajra_logo

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
        # Print the Vajra logo
        print_vajra_logo()

        # Handle resource allocation at the engine level
        resource_mapping = config.replica_resource_mapping
        if resource_mapping is None:
            resource_allocator = ResourceAllocator()
            resource_allocator.validate_cluster_resources(
                config.controller_config.num_replicas,
                config.controller_config.replica_controller_config.parallel_config.world_size,
            )
            resource_mapping = resource_allocator.get_replicaset_resource_mapping(
                config.controller_config.num_replicas,
                config.controller_config.replica_controller_config.parallel_config.world_size,
            )
            pretty_print_resource_mapping(resource_mapping)

        self.controller = ControllerFactory.create_replicaset_controller(
            config=config.controller_config,
            resource_mapping=resource_mapping,
            output_dir=config.output_dir,
        )

    def add_request(
        self,
        prompt: str,
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
    ) -> None:
        """Add a request to be processed.

        Args:
            prompt: The input text prompt
            sampling_params: Parameters controlling text generation
            prompt_token_ids: Optional pre-tokenized prompt
            seq_id: Optional unique identifier for the request
        """
        self.controller.add_request(
            prompt=prompt,
            sampling_params=sampling_params,
            prompt_token_ids=prompt_token_ids,
            seq_id=seq_id,
        )

    def get_outputs(self, block: bool = False) -> List[RequestOutput]:
        """Get any available outputs from processed requests.

        Returns:
            List of RequestOutput objects containing generated text and metadata
        """
        return self.controller.step(block=block)

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
        self.controller.pull_worker_metrics()
        self.controller.plot_metrics()
