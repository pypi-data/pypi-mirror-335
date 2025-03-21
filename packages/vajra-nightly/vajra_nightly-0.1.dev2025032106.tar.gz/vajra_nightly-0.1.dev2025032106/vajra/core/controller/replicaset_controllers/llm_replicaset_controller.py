import copy
import os
import time
from queue import Empty, Queue
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple

import ray  # type: ignore

from vajra.config import (
    LlmReplicaControllerConfig,
    LlmReplicasetControllerConfig,
)
from vajra.core.controller.replicaset_controllers.base_replicaset_controller import (
    BaseReplicasetController,
)
from vajra.core.scheduler.replicaset_schedulers import (
    BaseReplicasetScheduler,
    PullReplicasetScheduler,
    RoundRobinReplicasetScheduler,
)
from vajra.core.tokenizer.tokenizer_worker import TokenizerWorker
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import SequenceParams  # type: ignore
from vajra.datatypes import TokenizerInput  # type: ignore
from vajra.datatypes import TokenizerOutput  # type: ignore
from vajra.enums import (
    ReplicasetSchedulerType,
)
from vajra.logger import init_logger
from vajra.metrics_store import MetricsStore
from vajra.transformers_utils.tokenizer import get_hf_tokenizer
from vajra.utils import Counter

logger = init_logger(__name__)


class LLMReplicasetController(BaseReplicasetController):
    """An LLM Replica Set Controller that manages multiple replicas."""

    def __init__(
        self,
        config: LlmReplicasetControllerConfig,
        resource_mapping: Optional[Dict[int, List[Tuple[str, int]]]] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize LLMReplicasetController

        Args:
            config: Replica Set configuration containing resource mapping and other settings
        """
        self.replicaset_config = config
        self.replica_config = config.replica_controller_config
        self.output_dir = output_dir

        self._verify_config()

        # Resource mapping should be provided in the config
        assert resource_mapping is not None, (
            "Resource mapping must be provided in LlmReplicasetControllerConfig. "
            "Resources should be allocated at the engine level before controller initialization."
        )
        self.replica_resource_mapping = resource_mapping

        self.aggregate_metrics_store = self._create_aggregate_metrics_store()

        self.global_output_queue: Queue = Queue()

        # Initialize scheduler
        self.scheduler = self._create_scheduler()
        self.scheduler.init_queue()

        # Initialize replicas and tokenizer threads
        self._init_replica_controllers()

        self.tokenizer = get_hf_tokenizer(
            self.replica_config.model_config.model,
            trust_remote_code=self.replica_config.model_config.trust_remote_code,
            revision=self.replica_config.model_config.revision,
        )

        self.seq_counter = Counter()
        self.tokenizer_input_queue: Queue = Queue()
        self.tokenizer_output_queue: Queue = Queue()
        self.tokenizer_pool: List[TokenizerWorker] = []
        for _ in range(config.num_tokenizer_workers):
            worker = TokenizerWorker(
                self.tokenizer_input_queue,
                self.tokenizer_output_queue,
                self.tokenizer,
            )
            worker.start()
            self.tokenizer_pool.append(worker)

        # create a daemon thread to process the tokenizer output
        self.tokenizer_output_thread = Thread(
            target=self.process_tokenizer_output_loop, daemon=True
        )
        self.tokenizer_output_thread.start()
        # Profiling state
        self.profiling = False
        self.start_controller_execution()

    def _verify_config(self) -> None:
        """Verify configuration parameters"""

        self.replica_config.model_config.verify_with_parallel_config(
            self.replica_config.parallel_config
        )

        logger.info(
            "Initializing LLMReplicasetController with config: "
            f"model={self.replica_config.model_config.model!r}, "
            f"dtype={self.replica_config.model_config.dtype}, "
            f"tensor_parallel_size={self.replica_config.parallel_config.tensor_parallel_size}, "
            f"pipeline_parallel_size={self.replica_config.parallel_config.pipeline_parallel_size}, "
            f"num_replicas={self.replicaset_config.num_replicas}, "
            f"seed={self.replica_config.model_config.seed})"
        )

    def _create_scheduler(self) -> BaseReplicasetScheduler:
        """Create appropriate scheduler based on config"""
        scheduler_type = self.replicaset_config.replicaset_scheduler_config.get_type()
        if scheduler_type == ReplicasetSchedulerType.PULL:
            return PullReplicasetScheduler(
                self.replicaset_config, self.replicaset_config.num_replicas
            )
        elif scheduler_type == ReplicasetSchedulerType.ROUND_ROBIN:
            return RoundRobinReplicasetScheduler(
                self.replicaset_config, self.replicaset_config.num_replicas
            )
        else:
            raise ValueError(f"Unknown scheduler type: {scheduler_type}")

    def _init_replica_controllers(self) -> None:
        """Initialize LLM controllers for each replica"""
        self.replica_controllers: Dict[int, Any] = {}
        # Ensure output_dir exists and is not None
        output_base_dir = self.output_dir or "."
        os.makedirs(output_base_dir, exist_ok=True)

        for replica_id in range(self.replicaset_config.num_replicas):
            replica_config = copy.deepcopy(self.replica_config)

            # Create LlmReplicaControllerConfig from replica_config
            controller_config = LlmReplicaControllerConfig(
                model_config=replica_config.model_config,
                parallel_config=replica_config.parallel_config,
                cache_config=replica_config.cache_config,
                scheduler_config=replica_config.scheduler_config,
                worker_config=replica_config.worker_config,
                metrics_config=replica_config.metrics_config,
            )

            # Create replica output directory path
            replica_output_dir = output_base_dir if output_base_dir else None

            # Import the factory only when needed to avoid circular imports
            from vajra.core.controller.controller_factory import ControllerFactory

            replica_controller = ControllerFactory.create_llm_replica_controller(
                replica_id=replica_id,
                config=controller_config,
                resources=self.replica_resource_mapping[replica_id],
                waiting_queue=self.scheduler.get_replica_queue(replica_id),
                global_output_queue=self.global_output_queue,
                output_dir=replica_output_dir,
            )

            self.replica_controllers[replica_id] = replica_controller
            self.scheduler.set_replica_controller(replica_id, replica_controller)

    def process_tokenizer_output_loop(self) -> None:
        while True:
            tokenizer_output = self.tokenizer_output_queue.get()
            # Create the sequences.
            block_size = self.replica_config.cache_config.block_size
            eos_token_id = self.tokenizer.eos_token_id

            assert isinstance(eos_token_id, int)

            seq_params = SequenceParams(
                tokenizer_output.seq_id,
                tokenizer_output.prompt,
                tokenizer_output.prompt_token_ids,
                block_size,
                eos_token_id,
                tokenizer_output.arrival_time,
                tokenizer_output.sampling_params,
            )
            seq = Sequence(seq_params)
            # Trigger seq assignment to a replica
            self.scheduler.assign_seq_replica(seq)

    def add_request(
        self,
        prompt: Optional[str],
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
        arrival_time: Optional[float] = None,
    ) -> None:
        """Add a new generation request"""
        arrival_time = time.time()

        if not seq_id:
            seq_id = str(next(self.seq_counter))

        if prompt_token_ids is None:
            self.tokenizer_input_queue.put(
                TokenizerInput(
                    seq_id,
                    arrival_time,
                    prompt or "",
                    sampling_params,
                )
            )
        else:
            self.tokenizer_output_queue.put(
                TokenizerOutput(
                    seq_id,
                    arrival_time,
                    prompt or "",
                    prompt_token_ids,
                    sampling_params,
                )
            )

    def step(self, block: bool = False) -> List[RequestOutput]:
        """Process one step of generation and return outputs

        Args:
            block: If True, block until output is available. If False, return empty list if no output is available.

        Returns:
            List of RequestOutput objects from the queue or empty list if non-blocking and queue is empty.
        """
        try:
            return self.global_output_queue.get(block=block)
        except Empty:
            return []

    def start_controller_execution(self) -> None:
        """Start all replica controllers (alias for start)"""

        for controller in self.replica_controllers.values():
            print("starting controller for replica", controller.replica_id)
            controller.start_controller_execution()

    # Metrics related methods
    def _create_aggregate_metrics_store(self) -> MetricsStore:
        """Create metrics store for aggregating replica metrics"""
        metrics_store = MetricsStore.get_or_create_instance(
            self.replicaset_config.num_replicas + 1,
            self.replica_config,
            self.output_dir or "",
        )
        metrics_store.mark_initial_memory_profiling_done()
        return metrics_store

    def get_metric_store(self) -> MetricsStore:
        for controller in self.replica_controllers.values():
            self.aggregate_metrics_store.merge(controller.get_metric_store())
        return self.aggregate_metrics_store

    def reset_metrics(self) -> None:
        """Reset metrics for all replicas"""
        self.aggregate_metrics_store.reset()
        for controller in self.replica_controllers.values():
            controller.reset_metrics()

    # Profiling methods
    def start_profiling(self):
        """Start profiling all replicas"""
        self.profiling = True
        for controller in self.replica_controllers.values():
            controller.start_profiling()

    def stop_profiling(self):
        """Stop profiling all replicas"""
        self.profiling = False
        for controller in self.replica_controllers.values():
            controller.stop_profiling()

    # Metrics methods
    def pull_worker_metrics(self) -> None:
        """Pull metrics from all replica workers"""
        for controller in self.replica_controllers.values():
            controller.pull_worker_metrics()

    def get_replica_metrics_store(self, replica_id: int) -> MetricsStore:
        """Get metrics store for a specific replica"""
        return self.replica_controllers[replica_id].get_metric_store()

    def _reset_replica_metrics(self, replica_id: int) -> None:
        """Reset metrics for a specific replica"""
        self.replica_controllers[replica_id].reset_metrics()

    def has_unfinished_requests(self) -> bool:
        """Check if there are any unfinished requests"""
        return self.scheduler.has_unfinished_requests()

    def get_num_unfinished_requests(self) -> int:
        """Get number of unfinished requests"""
        return self.scheduler.get_num_unfinished_requests()

    def plot_metrics(self) -> None:
        self.get_metric_store().plot()

    def get_model_config(self) -> Any:
        """Return the model configuration for this replica set.

        This is required by the AbstractController interface.
        """
        return self.replica_config.model_config
