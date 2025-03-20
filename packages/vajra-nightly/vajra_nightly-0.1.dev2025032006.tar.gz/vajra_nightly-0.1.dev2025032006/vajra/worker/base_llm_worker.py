"""A GPU LLM worker class."""

import os
import time
from typing import Optional, Tuple, cast

import torch
import torch.distributed
import zmq

from vajra.config import (
    BaseReplicaControllerConfig,
    CacheConfig,
    LlmReplicaControllerConfig,
    ParallelConfig,
)
from vajra.core.sequence_manager import WorkerSequenceManager  # type: ignore
from vajra.core.sequence_manager import WorkerSequenceManagerParams  # type: ignore
from vajra.datatypes import SamplerOutputs  # type: ignore
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import (
    CommInfo,
    StepOutputs,
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepInputs as StepInputsProto,  # type: ignore
)
from vajra.enums import ReplicaControllerType
from vajra.logger import init_logger
from vajra.metrics_store import CpuTimer, MetricsStore, MetricType  # type: ignore
from vajra.model_executor import set_random_seed
from vajra.model_executor.llm_model_runner import LLMModelRunner
from vajra.model_executor.parallel_utils.parallel_state import (
    get_kv_parallel_rank,
    get_kv_parallel_world_size,
    get_pipeline_model_parallel_rank,
    get_rank,
    get_tensor_model_parallel_rank,
    initialize_model_parallel,
)
from vajra.utils.threading_utils import exit_on_error, synchronized
from vajra.utils.zmq_helper import ZMQHelper
from vajra.worker.base_worker import BaseWorker
from vajra.worker.cache_engine import CacheEngine

logger = init_logger(__name__)


_READY_ACK_WAIT_TIME = 1


class BaseLLMWorker(BaseWorker):
    """A worker class that executes (a partition of) the model on a GPU.

    Each worker is associated with a single GPU. The worker is responsible for
    maintaining the KV cache and executing the model on the GPU. In case of
    distributed inference, each worker is assigned a partition of the model.
    """

    def __init__(
        self,
        replica_id: int,
        config: BaseReplicaControllerConfig,
        local_rank: int,
        rank: int,
        comm_info: CommInfo,
        output_dir: Optional[str] = None,
    ) -> None:
        super().__init__(
            replica_id=replica_id,
            config=config,
            local_rank=local_rank,
            rank=rank,
            comm_info=comm_info,
            output_dir=output_dir,
        )
        assert self.config.get_type() in [
            ReplicaControllerType.LLM_BASE,
            ReplicaControllerType.LLM_PIPELINE_PARALLEL,
        ], "BaseLLMWorker must be initialized with a LlmReplicaControllerConfig"
        self.config = cast(LlmReplicaControllerConfig, self.config)
        # Setting up BaseLLMWorker specific parts like cache engine, sequence manager
        # Uninitialized cache engine. Will be initialized by
        # self.init_cache_engine().
        self.cache_engine: Optional[CacheEngine] = None
        self.gpu_cache: Optional[list] = None
        # Sequence manager also needs number of blocks for initialization
        self.seq_manager: Optional[WorkerSequenceManager] = None

    def _init_worker_timers(self) -> None:
        self.on_schedule_handling_timer = CpuTimer(
            MetricType.WORKER_ON_SCHEDULE_HANDLING, self.rank
        )
        self.on_step_completed_handling_timer = CpuTimer(
            MetricType.WORKER_ON_STEP_COMPLETE_HANDLING, self.rank
        )

    def _init_zmq_sockets(self):
        self.zmq_context = zmq.Context()
        self.enqueue_socket = self.zmq_context.socket(zmq.SUB)
        self.enqueue_socket.connect(
            f"tcp://{self.comm_info.engine_ip_address}:{self.comm_info.enqueue_socket_port}"
        )
        self.enqueue_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.output_socket = self.zmq_context.socket(zmq.PUSH)
        self.output_socket.connect(
            f"tcp://{self.comm_info.engine_ip_address}:{self.comm_info.output_socket_port}"
        )

    def _verify_parallel_config(self) -> None:
        assert self.config.parallel_config.pipeline_parallel_size == 1

    @torch.inference_mode()
    @synchronized
    def init_model(self):
        # torch.distributed.all_reduce does not free the input tensor until
        # the synchronization point. This causes the memory usage to grow
        # as the number of all_reduce calls increases. This env var disables
        # this behavior.
        # Related issue:
        # https://discuss.pytorch.org/t/cuda-allocation-lifetime-for-inputs-to-distributed-all-reduce/191573
        os.environ["TORCH_NCCL_AVOID_RECORD_STREAMS"] = "1"
        os.environ["KINETO_LOG_LEVEL"] = "5"
        # os.environ["NCCL_DEBUG"] = "INFO"
        # This env var set by Ray causes exceptions with graph building.
        os.environ.pop("NCCL_ASYNC_ERROR_HANDLING", None)

        logger.info(f"Worker {self.rank} is using device {self.local_rank}")
        self.device = torch.device(f"cuda:{self.local_rank}")
        torch.cuda.set_device(self.device)

        # Initialize the distributed environment.
        _init_distributed_environment(
            self.config.parallel_config,
            self.rank,
            self.comm_info.distributed_init_method,
        )

        self.tensor_model_parallel_rank = get_tensor_model_parallel_rank()
        self.pipeline_model_parallel_rank = get_pipeline_model_parallel_rank()
        self.kv_parallel_rank = get_kv_parallel_rank()

        self.is_tensor_parallel_rank_zero = self.tensor_model_parallel_rank == 0
        self.is_first_pipeline_stage = self.pipeline_model_parallel_rank == 0
        self.is_last_pipeline_stage = (
            self.pipeline_model_parallel_rank
            == self.config.parallel_config.pipeline_parallel_size - 1
        )

        logger.info(
            f"Initializing worker {self.rank} on device {self.device}, "
            f"tensor parallel rank {self.tensor_model_parallel_rank} "
            f"and pipeline parallel rank {self.pipeline_model_parallel_rank} "
            f"and cache parallel rank {self.kv_parallel_rank}."
        )

        # Initialize the model.
        set_random_seed(self.config.model_config.seed)
        self.model_runner = LLMModelRunner(
            self.config,
            self.device,
            self.rank,
        )
        logger.info(f"Model initialized on worker {self.rank}.")

    def _get_seq_manager_impl(self):
        return WorkerSequenceManager

    @torch.inference_mode()
    @synchronized
    def init_cache_engine(self, cache_config: CacheConfig) -> None:
        torch.cuda.set_device(self.device)

        self.config.update_cache_config(cache_config)

        self.cache_engine = CacheEngine(
            self.config,
        )
        self.gpu_cache = self.cache_engine.gpu_cache

        self.seq_manager = self._get_seq_manager_impl()(
            WorkerSequenceManagerParams(
                enable_sequence_pipeline_parallel=self.config.parallel_config.enable_sequence_pipeline_parallel,
                block_size=self.config.cache_config.block_size,
                num_gpu_blocks=self.config.cache_config.num_gpu_blocks,
                max_model_len=self.config.model_config.max_model_len,
                max_num_tokens_per_kvp_group=self.config.parallel_config.max_num_tokens_per_kvp_group,
                rank=get_rank(),
                kvp_group_id=get_kv_parallel_rank(),
                kvp_parallel_world_size=get_kv_parallel_world_size(),
            ),
        )

        self.execution_thread.start()

    def wait_till_ready(self) -> None:
        self.worker_ready_event.wait()
        time.sleep(_READY_ACK_WAIT_TIME)

    @synchronized
    def get_model_parallel_ranks(self) -> Tuple[int, int, int]:
        return (
            self.tensor_model_parallel_rank,
            self.pipeline_model_parallel_rank,
            self.kv_parallel_rank,
        )

    def on_step_completed(
        self,
        scheduler_output: SchedulerOutput,
        sampler_outputs: Optional[SamplerOutputs],
    ) -> None:
        assert self.seq_manager is not None
        assert sampler_outputs is not None

        self.seq_manager.on_step_completed(
            scheduler_output.seq_schedule_metadata_list, sampler_outputs
        )

    @torch.inference_mode()
    def execute_model(
        self,
        scheduler_output: SchedulerOutput,
    ) -> Optional[SamplerOutputs]:
        assert self.seq_manager is not None

        torch.cuda.synchronize()
        batch_stage_start_time = time.time()

        self.metrics_store.on_batch_stage_start(scheduler_output)

        with self.on_schedule_handling_timer:
            _, seqs, seq_metadata_list = self.seq_manager.on_schedule_worker(
                scheduler_output
            )

        sampler_outputs = self.model_runner.run(
            seqs,
            seq_metadata_list,
            self.gpu_cache,
        )

        assert sampler_outputs is not None

        with self.on_step_completed_handling_timer:
            self.on_step_completed(scheduler_output, sampler_outputs)

        torch.cuda.synchronize()

        batch_stage_end_time = time.time()

        self.metrics_store.on_batch_stage_end(
            seq_metadata_list,
            self.tensor_model_parallel_rank,
            self.pipeline_model_parallel_rank,
            self.kv_parallel_rank,
            batch_stage_start_time,
            batch_stage_end_time,
        )

        return sampler_outputs

    @exit_on_error
    def _execution_loop(self) -> None:
        assert self.seq_manager is not None

        torch.cuda.set_device(self.device)

        self.worker_ready_event.set()

        while True:
            step_inputs = ZMQHelper.recv_pyobj(self.enqueue_socket, StepInputsProto)

            for params in step_inputs.new_seq_params:  # type: ignore
                new_seq = Sequence(params)
                self.seq_manager.add_seq(new_seq)

            output = self.execute_model(step_inputs.scheduler_output)

            if not self.is_tensor_parallel_rank_zero:
                continue

            assert output is not None

            step_outputs = StepOutputs(
                step_inputs.scheduler_output.id,
                output,
            )
            ZMQHelper.send_pyobj(self.output_socket, step_outputs)

    @synchronized
    def get_metrics_store(self) -> MetricsStore:
        return self.metrics_store

    @synchronized
    def mark_initial_memory_profiling_done(self):
        self.metrics_store.mark_initial_memory_profiling_done()

    @synchronized
    def reset_metrics(self) -> None:
        self.metrics_store.reset()

    @synchronized
    def start_profiling(self) -> None:
        self.profiler = torch.profiler.profile(
            activities=[
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ],
        )
        self.profiler.__enter__()

    @synchronized
    def profile_num_available_blocks(
        self,
        block_size: int,
        gpu_memory_utilization: float,
    ) -> int:
        return self.model_runner.profile_num_available_blocks(
            block_size, gpu_memory_utilization
        )

    @synchronized
    def stop_profiling(self) -> None:
        self.profiler.__exit__(None, None, None)
        self.profiler.export_chrome_trace(
            f"{self.output_dir}/profiler_trace_rank_{self.rank}.json"
        )


def _init_distributed_environment(
    parallel_config: ParallelConfig,
    rank: int,
    distributed_init_method: str,
) -> None:
    """Initialize the distributed environment."""
    if torch.distributed.is_initialized():
        torch_world_size = torch.distributed.get_world_size()
        if torch_world_size != parallel_config.world_size:
            raise RuntimeError(
                "torch.distributed is already initialized but the torch world "
                "size does not match parallel_config.world_size "
                f"({torch_world_size} vs. {parallel_config.world_size})."
            )
    else:
        torch.distributed.init_process_group(
            backend="nccl",
            world_size=parallel_config.world_size,
            rank=rank,
            init_method=distributed_init_method,
        )

    initialize_model_parallel(
        parallel_config.tensor_parallel_size,
        parallel_config.pipeline_parallel_size,
        parallel_config.kv_parallel_size,
    )

    # A small all_reduce for warmup.
    torch.distributed.all_reduce(torch.zeros(1).cuda())
