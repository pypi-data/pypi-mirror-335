from queue import Queue
from threading import Thread
from typing import Dict

from vajra._native.core.tokenizer import (  # type: ignore
    TokenizerPool,
    TokenizerPoolInput,
    TokenizerPoolOutput,
)
from vajra.config import (
    LlmReplicasetControllerConfig,
    ModelConfig,
)
from vajra.core.controller.replica_controllers import ReplicaControllerRegistry
from vajra.core.controller.replica_controllers.base_replica_controller import (
    BaseReplicaController,
)
from vajra.core.controller.replicaset_controllers.base_replicaset_controller import (
    BaseReplicasetController,
)
from vajra.core.scheduler.replicaset_schedulers import ReplicasetSchedulerRegistry
from vajra.core.scheduler.request_prioritizers import RequestPrioritizerRegistry
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import SequenceParams  # type: ignore
from vajra.datatypes import UserSequenceParams  # type: ignore
from vajra.datatypes import (
    GlobalResourceMapping,
)
from vajra.logger import init_logger
from vajra.metrics_store import EngineMetricsStore, MetricsStoreHandle
from vajra.transformers_utils.tokenizer import get_eos_token_id, get_tokenizer_path
from vajra.utils.threading_utils import exit_on_error

logger = init_logger(__name__)


class LLMReplicasetController(BaseReplicasetController):
    """An LLM Replica Set Controller that manages multiple replicas."""

    def __init__(
        self,
        config: LlmReplicasetControllerConfig,
        global_resource_mapping: GlobalResourceMapping,
        waiting_seq_queue: Queue[UserSequenceParams],
        output_queue: Queue[RequestOutput],
    ) -> None:
        """
        Initialize the LLMReplicasetController
        Args:
            config: Replica Set configuration containing resource mapping and other settings
            global_resource_mapping: Mapping of resources to replicas
            waiting_seq_queue: Queue to which waiting sequences are sent
            output_queue: Queue to which outputs are sent
        """
        super().__init__(
            config,
            global_resource_mapping,
            waiting_seq_queue,
            output_queue,
        )

        self._verify_config()

        # Resource mapping should be provided in the config
        assert global_resource_mapping is not None
        self.global_resource_mapping = global_resource_mapping

        # Initialize scheduler
        self.scheduler = ReplicasetSchedulerRegistry.get(
            self.config.replicaset_scheduler_config.get_type(),
            self.config.replicaset_scheduler_config,
            self.config.num_replicas,
        )
        self.request_prioritizer = RequestPrioritizerRegistry.get(
            self.config.request_prioritizer_config.get_type(),
            self.config.request_prioritizer_config,
            self.replica_controller_config.model_config,
            self.replica_controller_config.cache_config,
            self.replica_controller_config.parallel_config,
            self.replica_controller_config.scheduler_config,
        )

        # Initialize replicas and tokenizer threads
        self._init_replica_controllers()

        self.metrics_store = MetricsStoreHandle.get_instance()

        self.eos_token_id = get_eos_token_id(
            self.replica_controller_config.model_config.model,
            trust_remote_code=self.replica_controller_config.model_config.trust_remote_code,
            revision=self.replica_controller_config.model_config.revision,
        )
        assert isinstance(self.eos_token_id, int)

        self.tokenizer_pool = TokenizerPool(
            get_tokenizer_path(
                self.replica_controller_config.model_config.model,
                revision=self.replica_controller_config.model_config.revision,
            ),
            config.num_tokenizer_workers,
        )
        self.tokenizer_pool.start()
        print("STARTED THE POOL!!")

        # create a daemon thread to process the tokenizer output
        self.tokenizer_output_thread = Thread(
            target=self._process_tokenizer_output_loop, daemon=True
        )
        self.tokenizer_output_thread.start()

        self.input_queue_watch_thread = Thread(
            target=self._input_queue_watch_loop, daemon=True
        )
        self.input_queue_watch_thread.start()

    def _verify_config(self) -> None:
        """Verify configuration parameters"""

        self.replica_controller_config.model_config.verify_with_parallel_config(
            self.replica_controller_config.parallel_config
        )

        logger.info(
            "Initializing LLMReplicasetController with config: "
            f"model={self.replica_controller_config.model_config.model!r}, "
            f"dtype={self.replica_controller_config.model_config.dtype}, "
            f"tensor_parallel_size={self.replica_controller_config.parallel_config.tensor_parallel_size}, "
            f"pipeline_parallel_size={self.replica_controller_config.parallel_config.pipeline_parallel_size}, "
            f"num_replicas={self.config.num_replicas}, "
            f"seed={self.replica_controller_config.model_config.seed})"
        )

    def _init_replica_controllers(self) -> None:
        """Initialize LLM controllers for each replica"""
        self.replica_controllers: Dict[int, BaseReplicaController] = {}

        for replica_id in range(self.config.num_replicas):
            self.replica_controllers[replica_id] = ReplicaControllerRegistry.get(
                self.replica_controller_config.get_type(),
                replica_id,
                self.replica_controller_config,
                self.global_resource_mapping[replica_id],
                self.request_prioritizer,
                self.scheduler.get_replica_queue(replica_id),
                self.output_queue,
            )

    @exit_on_error
    def _process_tokenizer_output_loop(self) -> None:
        block_size = self.replica_controller_config.cache_config.block_size

        while True:
            tokenizer_output = self.tokenizer_pool.get_output()
            seq_params = SequenceParams(
                tokenizer_output.seq_id,
                tokenizer_output.prompt,
                tokenizer_output.token_ids,
                block_size,
                self.eos_token_id,
                tokenizer_output.arrival_time,
                tokenizer_output.sampling_params,
            )
            seq = Sequence(seq_params)
            seq_with_priority = self.request_prioritizer.get_seq_with_priority(seq)
            # insert the sequence into the replica controller queue
            self.scheduler.schedule(seq_with_priority)

    @exit_on_error
    def _input_queue_watch_loop(self) -> None:
        while True:
            user_seq_params = self.waiting_seq_queue.get()
            """Add a new generation request"""
            if not user_seq_params.prompt_token_ids:
                self.tokenizer_pool.add_request(
                    TokenizerPoolInput(
                        user_seq_params.seq_id,
                        user_seq_params.arrival_time,
                        user_seq_params.prompt,
                        user_seq_params.sampling_params,
                    )
                )
            else:
                self.tokenizer_pool.add_output(
                    TokenizerPoolOutput(
                        user_seq_params.seq_id,
                        user_seq_params.arrival_time,
                        user_seq_params.prompt,
                        user_seq_params.prompt_token_ids,
                        user_seq_params.sampling_params,
                    )
                )

    def get_metric_store(self) -> EngineMetricsStore:
        assert isinstance(self.metrics_store, EngineMetricsStore)

        for controller in self.replica_controllers.values():
            self.metrics_store.merge(controller.get_metric_store())
        return self.metrics_store

    def reset_metrics(self) -> None:
        """Reset metrics for all replicas"""
        self.metrics_store.reset()
        for controller in self.replica_controllers.values():
            controller.reset_metrics()

    def get_model_config(self) -> ModelConfig:
        """Return the model configuration for this replica set.

        This is required by the AbstractController interface.
        """
        return self.replica_controller_config.model_config
