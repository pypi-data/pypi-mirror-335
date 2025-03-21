from queue import PriorityQueue, Queue
from typing import Dict, List, Optional, Tuple, cast

from vajra.config import (
    BaseReplicasetControllerConfig,
    LlmReplicaControllerConfig,
    LlmReplicasetControllerConfig,
)
from vajra.core.controller.replica_controllers import BaseReplicaController
from vajra.core.controller.replicaset_controllers import BaseReplicasetController
from vajra.enums import ReplicasetControllerType


class ControllerFactory:
    """Factory class for creating Vajra controllers based on configuration."""

    @classmethod
    def create_llm_replica_controller(
        cls,
        replica_id: int,
        config: LlmReplicaControllerConfig,
        resources: Optional[List[Tuple[str, int]]] = None,
        waiting_queue: Optional[PriorityQueue] = None,
        global_output_queue: Optional[Queue] = None,
        output_dir: Optional[str] = None,
    ) -> BaseReplicaController:
        """Creates an appropriate Vajra controller based on the system configuration.

        Args:
            config: The system configuration specifying model, parallel strategy etc.
            waiting_queue: Optional queue for waiting sequences
            global_output_queue: Optional queue for global outputs

        Returns:
            An instance of AbstractController based on the parallel config.
        """
        if config.parallel_config.pipeline_parallel_size > 1:
            # Dynamic import to avoid circular dependency
            from vajra.core.controller.replica_controllers.pipeline_parallel_llm_replica_controller import (
                PipelineParallelLLMReplicaController,
            )

            assert isinstance(config, LlmReplicaControllerConfig)
            return PipelineParallelLLMReplicaController(
                replica_id=replica_id,
                config=config,
                resources=resources,
                waiting_queue=waiting_queue,
                global_output_queue=global_output_queue,
                output_dir=output_dir,
            )
        else:
            # Dynamic import to avoid circular dependency
            from vajra.core.controller.replica_controllers.base_llm_replica_controller import (
                BaseLLMReplicaController,
            )

            return BaseLLMReplicaController(
                replica_id=replica_id,
                config=config,
                resources=resources,
                waiting_queue=waiting_queue,
                global_output_queue=global_output_queue,
                output_dir=output_dir,
            )

    @classmethod
    def create_replicaset_controller(
        cls,
        config: BaseReplicasetControllerConfig,
        resource_mapping: Optional[Dict[int, List[Tuple[str, int]]]] = None,
        output_dir: Optional[str] = None,
    ) -> BaseReplicasetController:
        """Creates an appropriate Vajra replica set controller based on the system configuration."""
        # Dynamic import to avoid circular dependency
        if config.get_type() == ReplicasetControllerType.LLM:
            from vajra.core.controller.replicaset_controllers.llm_replicaset_controller import (
                LLMReplicasetController,
            )

            assert isinstance(config, LlmReplicasetControllerConfig)
            return LLMReplicasetController(
                config=cast(LlmReplicasetControllerConfig, config),
                resource_mapping=resource_mapping,
                output_dir=output_dir,
            )

        # If we get here, we have an unsupported controller type
        raise ValueError(
            f"Unsupported replicaset controller type: {config.get_type()}. "
            f"Currently only {ReplicasetControllerType.LLM} is supported."
        )
