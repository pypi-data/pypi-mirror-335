import math
import time
from functools import partial
from queue import PriorityQueue, Queue
from threading import Event, Thread
from typing import Any, Dict, List, Optional, Tuple

import zmq

from vajra.config import LlmReplicaControllerConfig, ModelConfig
from vajra.core.controller.ray_utils import RayWorker, initialize_cluster, ray
from vajra.core.controller.replica_controllers.base_replica_controller import (
    BaseReplicaController,
)
from vajra.core.scheduler.replica_schedulers import ReplicaSchedulerRegistry
from vajra.core.sequence_manager import EngineSequenceManager  # type: ignore
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import SamplerOutputs  # type: ignore
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import SequenceParams  # type: ignore
from vajra.datatypes import SequenceScheduleMetadata  # type: ignore
from vajra.datatypes import (
    CommInfo,
    StepInputs,
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepOutputs as StepOutputsProto,  # type: ignore
)
from vajra.logger import init_logger
from vajra.metrics_store import MetricsStore
from vajra.transformers_utils.tokenizer import get_tokenizer
from vajra.utils import get_ip, unset_cuda_visible_devices
from vajra.utils.threading_utils import exit_on_error, synchronized
from vajra.utils.zmq_helper import ZMQHelper

logger = init_logger(__name__)

MAX_WORKER_CONCURRENCY = 1
MAX_ZMQ_RETRIES = 5
ZMQ_RETRY_DELAY = 1
SCHEDULER_LOOP_DELAY = 0.01

ModelParallelRank = Tuple[int, int, int]


class BaseLLMReplicaController(BaseReplicaController):
    """An LLM Replica Controller that receives requests and generates texts.

    This is the main class for the Vajra engine. It receives requests
    from clients and generates texts from the LLM. It includes a tokenizer, a
    language model (possibly distributed across multiple GPUs), and GPU memory
    space allocated for intermediate states (aka KV cache). This class utilizes
    iteration-level scheduling and efficient memory management to maximize the
    serving throughput.

    Args:
        config; System Config: The system configuration for the engine.
    """

    def __init__(
        self,
        replica_id: int,
        config: LlmReplicaControllerConfig,
        resources: Optional[List[Tuple[str, int]]] = None,
        waiting_queue: Optional[PriorityQueue] = None,
        global_output_queue: Optional[Queue] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        super().__init__(
            replica_id=replica_id,
            config=config,
            resources=resources,
            output_dir=output_dir,
        )

        logger.info(
            f"Initializing an LLM Controller [Replica {replica_id}] with config: "
            f"model={config.model_config.model!r}, "
            f"dtype={config.model_config.torch_dtype}, "
            f"tensor_parallel_size={config.parallel_config.tensor_parallel_size}, "
            f"pipeline_parallel_size={config.parallel_config.pipeline_parallel_size}, "
            f"kv_parallel_size={config.parallel_config.kv_parallel_size}, "
            f"enable_expert_parallel={config.parallel_config.enable_expert_parallel}, "
            f"seed={config.model_config.seed})"
        )

        self._verify_args()

        self.waiting_queue = (
            waiting_queue if waiting_queue is not None else PriorityQueue()
        )
        self.global_output_queue = (
            global_output_queue if global_output_queue is not None else Queue()
        )

        if global_output_queue is not None:
            # shared global output queue
            self.pull_event = Event()
            self.schedule_thread = Thread(target=self._schedule_loop, daemon=True)

        tokenizer = get_tokenizer(
            config.model_config.model,
            revision=config.model_config.revision,
        )
        self.seq_manager = EngineSequenceManager(
            tokenizer,
            config.parallel_config.enable_sequence_pipeline_parallel,
        )
        self.metrics_store = MetricsStore.get_or_create_instance(
            self.replica_id, self.config, self.output_dir or ""
        )
        self.worker_map: Dict[ModelParallelRank, int] = {}

        self.schedule_event = Event()

        self.scheduler_timer_thread = Thread(
            target=self._scheduler_timer_loop, daemon=True
        )

        # Initialize the cluster.
        initialize_cluster()

        self.comm_info = CommInfo(get_ip())

        # Create the parallel GPU workers.
        self._init_workers_ray()

        # Setup ZMQ communication channels
        self._init_zmq_sockets()

        # Profile the memory usage and initialize the cache.
        self._init_cache()

        # Initialize the worker map.
        self._init_worker_map()

        self._mark_initial_memory_profiling_done()

        # Create the scheduler.
        self.scheduler = ReplicaSchedulerRegistry.get(
            config.scheduler_config.get_type(),
            config.model_config,
            config.scheduler_config,
            config.cache_config,
            config.parallel_config,
            self.waiting_queue,
        )

        self.has_started_execution_loops = False
        self.new_seq_params_queue = Queue()

        self._run_workers("wait_till_ready")

    def _bind_zmq_socket(self, socket: zmq.Socket, port: int):
        for attempt in range(MAX_ZMQ_RETRIES):
            try:
                socket.bind(f"tcp://*:{port}")
                break
            except zmq.ZMQError as e:
                if attempt < MAX_ZMQ_RETRIES - 1:
                    logger.info(
                        f"Failed to bind enqueue socket, retrying in {ZMQ_RETRY_DELAY} seconds..."
                    )
                    time.sleep(ZMQ_RETRY_DELAY)
                else:
                    raise Exception(
                        f"Failed to bind enqueue socket after {MAX_ZMQ_RETRIES} attempts"
                    ) from e

    def _init_zmq_sockets(self):
        self.zmq_context = zmq.Context()
        self.enqueue_socket = self.zmq_context.socket(zmq.PUB)
        self._bind_zmq_socket(self.enqueue_socket, self.comm_info.enqueue_socket_port)
        self.output_socket = self.zmq_context.socket(zmq.PULL)
        self._bind_zmq_socket(self.output_socket, self.comm_info.output_socket_port)

    def _validate_parallel_config(self) -> None:
        assert self.config.parallel_config.pipeline_parallel_size == 1

    def _get_worker_impl(self):
        # Lazy import the Worker to avoid importing torch.cuda/xformers
        # before CUDA_VISIBLE_DEVICES is set in the Worker
        from vajra.worker.base_llm_worker import (
            BaseLLMWorker,  # pylint: disable=import-outside-toplevel
        )

        return BaseLLMWorker

    def _init_workers_ray(self, **ray_remote_kwargs):
        # Resources must be set by the InferenceEngine before controller initialization
        assert self.resources is not None, (
            "Resources not set in controller config. "
            "Resources should be allocated at the engine level before controller initialization."
        )

        replica_resources = self.resources

        self.workers: List[RayWorker] = []

        unset_cuda_visible_devices()

        for rank, (node_ip, device_id) in enumerate(replica_resources):
            worker_class = ray.remote(
                num_cpus=1,
                # num_gpus=1, # we don't use ray for managing GPUs
                **ray_remote_kwargs,
            )(RayWorker)

            if node_ip:
                worker_class = worker_class.options(
                    max_concurrency=MAX_WORKER_CONCURRENCY,
                    resources={
                        node_ip: 0.01,
                    },
                )
            else:
                worker_class = worker_class.options(
                    max_concurrency=MAX_WORKER_CONCURRENCY,
                )

            worker = worker_class.remote(self.config.model_config.trust_remote_code)  # type: ignore
            self.workers.append(worker)

        # Initialize torch distributed process group for the workers.
        config_for_worker = LlmReplicaControllerConfig(
            model_config=self.config.model_config,
            worker_config=self.config.worker_config,
            cache_config=self.config.cache_config,
            parallel_config=self.config.parallel_config,
            scheduler_config=self.config.scheduler_config,
            metrics_config=self.metrics_store.get_config_for_worker(),
        )

        worker_impl = self._get_worker_impl()

        for rank, (node_ip, device_id) in enumerate(replica_resources):
            worker = self.workers[rank]
            comm_info = self.comm_info
            replica_id = self.replica_id
            output_dir = self.output_dir
            promise = worker.init_worker.remote(  # type: ignore
                lambda rank=rank, local_rank=device_id: worker_impl(
                    replica_id=replica_id,
                    config=config_for_worker,
                    local_rank=local_rank,
                    rank=rank,
                    comm_info=comm_info,
                    output_dir=output_dir,
                )
            )
            ray.get(promise)

        self._run_workers(
            "init_model",
            get_all_outputs=True,
        )

    def _verify_args(self) -> None:
        self._validate_parallel_config()
        self.config.model_config.verify_with_parallel_config(
            self.config.parallel_config
        )

    def _get_blocks_per_request(self) -> int:
        if self.config.parallel_config.kv_parallel_size == 1:
            return math.ceil(
                self.config.model_config.max_model_len
                / self.config.cache_config.block_size
            )

        return math.ceil(
            self.config.parallel_config.max_num_tokens_per_kvp_group
            / self.config.cache_config.block_size
        )

    def _init_cache(self) -> None:
        """Profiles the memory usage and initializes the KV cache."""
        # Get the maximum number of blocks that can be allocated on GPU.
        num_gpu_blocks_across_workers = self._run_workers(
            "profile_num_available_blocks",
            get_all_outputs=True,
            block_size=self.config.cache_config.block_size,
            gpu_memory_utilization=self.config.worker_config.gpu_memory_utilization,
        )

        # Since we use a shared centralized controller, we take the minimum
        # number of blocks across all workers to make sure all the memory
        # operators can be applied to all workers.
        num_gpu_blocks = min(num_gpu_blocks_across_workers)
        # FIXME(woosuk): Change to debug log.
        logger.info(f"# GPU blocks: {num_gpu_blocks}")

        if num_gpu_blocks <= 0:
            raise ValueError(
                "No available memory for the cache blocks. "
                "Try increasing `gpu_memory_utilization` when "
                "initializing the engine."
            )
        max_blocks_per_request = self._get_blocks_per_request()
        if num_gpu_blocks < max_blocks_per_request:
            raise ValueError(
                f"Not enough available memory to schedule a request will maximum allowed length {self.config.model_config.max_model_len}. "
                f"Need {max_blocks_per_request}, available {num_gpu_blocks} gpu blocks. "
                f"Try decreasing `max_batch_size`, `max_model_len`."
            )
        self.config.cache_config.set_num_gpu_blocks(num_gpu_blocks)
        # Initialize the cache.
        self._run_workers(
            "init_cache_engine",
            cache_config=self.config.cache_config,
            get_all_outputs=True,
        )

    def _init_worker_map(self) -> None:
        model_parallel_ranks = self._run_workers(
            "get_model_parallel_ranks",
            get_all_outputs=True,
        )

        self.worker_map = {mp_rank: i for i, mp_rank in enumerate(model_parallel_ranks)}

    def _on_step_completed(
        self,
        scheduler_output: SchedulerOutput,
        ignored_seqs: List[Sequence],
        seqs: List[Sequence],
        sampler_outputs: SamplerOutputs,
        start_time: float,
    ) -> List[RequestOutput]:
        self.seq_manager.on_step_completed(
            scheduler_output.seq_schedule_metadata_list,
            sampler_outputs,
        )
        self.scheduler.on_step_completed(seqs, time.time() - start_time)

        end_time = time.time()

        self.metrics_store.on_batch_end(
            seqs=seqs,
            scheduler_output=scheduler_output,
            batch_start_time=start_time,
            batch_end_time=end_time,
        )
        all_request_outputs = self.seq_manager.generate_request_outputs(
            ignored_seqs, seqs
        )
        self.global_output_queue.put(all_request_outputs)
        return all_request_outputs

    def get_model_config(self) -> ModelConfig:
        return self.config.model_config

    def add_request(
        self,
        prompt: str,
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
    ) -> None:
        raise NotImplementedError(
            "add_request is not implemented for BaseLLMReplicaController"
        )

    @synchronized
    def _get_new_seq_params(self) -> List[SequenceParams]:
        new_seq_params = []
        while not self.new_seq_params_queue.empty():
            new_seq_params.append(self.new_seq_params_queue.get())
        return new_seq_params

    def get_num_unfinished_requests(self) -> int:
        """Gets the number of unfinished requests."""
        return self.scheduler.get_num_unfinished_seqs()

    def has_unfinished_requests(self) -> bool:
        """Returns True if there are unfinished requests."""
        return self.scheduler.has_unfinished_seqs()

    def _combine_sampler_outputs(
        self,
        all_workers_sampler_outputs: List[SamplerOutputs],
        seq_schedule_metadata_list: List[SequenceScheduleMetadata],
    ) -> SamplerOutputs:
        # Combine the outputs from all workers into a single dict, which maps
        # seq_id to the corresponding SamplerOutput.
        sampler_outputs_map = {
            output.seq_id: output
            for worker_outputs in all_workers_sampler_outputs
            for output in worker_outputs
            if output
        }

        return [sampler_outputs_map[s.seq_id] for s in seq_schedule_metadata_list]

    def step(self, block: bool = False) -> List[RequestOutput]:
        """Performs one decoding iteration and returns newly generated results.

        This function performs one decoding iteration of the engine. It first
        schedules the sequences to be executed in the next iteration.
        Then, it executes the model and updates the scheduler with the model outputs.
        Finally, it decodes the sequences and returns the newly generated results.

        Args:
            block: Whether to block until outputs are available (not used in this implementation)

        Returns:
            List of RequestOutput objects containing generated text and metadata
        """
        start_time = time.time()

        scheduler_output = self.scheduler.schedule()

        if scheduler_output.is_empty:
            return []
        ignored_seqs, seqs = self.seq_manager.on_schedule(scheduler_output)
        end_time = time.time()

        step_inputs = StepInputs(
            scheduler_output,
            new_seq_params=self._get_new_seq_params(),
        )

        ZMQHelper.send_pyobj(self.enqueue_socket, step_inputs)
        self.metrics_store.on_schedule(scheduler_output, start_time, end_time)

        all_sampler_outputs: List[SamplerOutputs] = []
        for _ in range(self.config.parallel_config.kv_parallel_size):
            step_outputs = ZMQHelper.recv_pyobj(self.output_socket, StepOutputsProto)
            assert step_outputs.schedule_id == scheduler_output.id
            all_sampler_outputs.append(step_outputs.sampler_outputs)

        combined_sampler_outputs = self._combine_sampler_outputs(
            all_sampler_outputs, scheduler_output.seq_schedule_metadata_list
        )

        return self._on_step_completed(
            scheduler_output,
            ignored_seqs,
            seqs,
            combined_sampler_outputs,
            start_time,
        )

    def on_controller_assignment(self, seq: Sequence) -> None:
        self.seq_manager.add_seq(seq)
        new_param = SequenceParams(
            seq_id=seq.seq_id,
            prompt=seq.prompt,
            prompt_token_ids=seq.prompt_token_ids,
            block_size=seq.block_size,
            eos_token_id=seq.eos_token_id,
            arrival_time=seq.arrival_time,
            sampling_params=seq.sampling_params,
        )
        self.new_seq_params_queue.put(new_param)  # Thread-safe operation
        self.schedule_event.set()
        self.metrics_store.on_request_arrival(seq)

    def start_controller_execution(self) -> None:
        if self.has_started_execution_loops:
            return
        self.schedule_event.set()
        self.scheduler_timer_thread.start()
        self.has_started_execution_loops = True
        self.schedule_thread.start()
        logger.info(
            f"Started for replica id {self.replica_id}:\n"
            "  1. Scheduler timer thread\n"
            "  2. Schedule thread"
        )

    def _run_workers(
        self,
        method: str,
        *args,
        get_all_outputs: bool = False,
        ignore_output: bool = False,
        **kwargs,
    ) -> Any:
        """Runs the given method on all workers."""
        all_outputs = []
        for worker in self.workers:
            executor = partial(worker.execute_method.remote, method)  # type: ignore

            output = executor(*args, **kwargs)
            all_outputs.append(output)

        if ignore_output:
            return

        while True:
            try:
                all_outputs = ray.get(all_outputs, timeout=0)
                break
            except ray.exceptions.GetTimeoutError:  # type: ignore
                time.sleep(0)
                continue

        if get_all_outputs:
            return all_outputs

        # Make sure all workers have the same results.
        output = all_outputs[0]
        for other_output in all_outputs[1:]:
            assert output == other_output
        return output

    def _run_worker(
        self,
        model_parallel_rank: ModelParallelRank,
        method: str,
        *args,
        **kwargs,
    ) -> Any:
        """Runs the given method on all workers."""
        worker = self.workers[self.worker_map[model_parallel_rank]]
        executor = partial(worker.execute_method.remote, method)  # type: ignore

        output = executor(*args, **kwargs)

        while True:
            try:
                output = ray.get(output, timeout=0)
                break
            except ray.exceptions.GetTimeoutError:  # type: ignore
                time.sleep(0)
                continue

        return output

    def plot_metrics(self) -> None:
        self.metrics_store.plot()

    def pull_worker_metrics(self) -> None:
        worker_metrics = self._run_workers(
            "get_metrics_store",
            get_all_outputs=True,
        )
        for worker_metric in worker_metrics:
            self.metrics_store.merge(worker_metric)

    @exit_on_error
    def _scheduler_timer_loop(self) -> None:
        while True:
            time.sleep(SCHEDULER_LOOP_DELAY)
            self.schedule_event.set()

    def _mark_initial_memory_profiling_done(self):
        self.metrics_store.mark_initial_memory_profiling_done()
        self._run_workers("mark_initial_memory_profiling_done", get_all_outputs=True)

    def reset_metrics(self) -> None:
        self.scheduler.reset_state()
        self.metrics_store.reset()
        self._run_workers("reset_metrics", get_all_outputs=True)

    def start_profiling(self) -> None:
        self._run_workers("start_profiling")

    def stop_profiling(self) -> None:
        self._run_workers("stop_profiling")

    def get_metric_store(self) -> MetricsStore:
        return self.metrics_store

    @exit_on_error
    def _schedule_loop(self):
        while True:
            self.schedule_event.wait()
            self.schedule_event.clear()
            outputs = self.step()
            self.schedule_event.set()
