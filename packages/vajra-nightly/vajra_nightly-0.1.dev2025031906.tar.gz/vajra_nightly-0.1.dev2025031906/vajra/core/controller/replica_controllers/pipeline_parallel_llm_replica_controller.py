import time
from collections import defaultdict
from dataclasses import dataclass
from queue import Empty, PriorityQueue, Queue
from threading import Thread
from typing import Any, Dict, List, NoReturn, Optional, Tuple

import zmq

from vajra.config import LlmReplicaControllerConfig
from vajra.core.controller.replica_controllers.base_llm_replica_controller import (
    BaseLLMReplicaController,
)
from vajra.datatypes import RequestOutput  # type: ignore
from vajra.datatypes import SamplerOutputs  # type: ignore
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import SequenceParams  # type: ignore
from vajra.datatypes import (
    StepInputs,
    StepMicrobatchOutputs,
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepMicrobatchOutputs as StepMicrobatchOutputsProto,  # type: ignore
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepOutputs as StepOutputsProto,  # type: ignore
)
from vajra.logger import init_logger
from vajra.utils.threading_utils import exit_on_error, synchronized
from vajra.utils.zmq_helper import ZMQHelper

logger = init_logger(__name__)


@dataclass(frozen=True)
class ScheduleStageOutputs:
    ignored_seqs: List[Sequence]
    seqs: List[Sequence]
    scheduler_output: SchedulerOutput
    start_time: float


class PipelineParallelLLMReplicaController(BaseLLMReplicaController):
    """An LLM controller that receives requests and generates texts.

    This controller receives requests
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
            waiting_queue=waiting_queue,
            global_output_queue=global_output_queue,
            output_dir=output_dir,
        )

        # Create the request queue.
        self.has_started_execution_loops = False
        self.scheduler_output_queue: Queue[ScheduleStageOutputs] = Queue()
        self.output_queue: Queue[List[RequestOutput]] = Queue()
        self.microbatch_watch_queue: Queue[SchedulerOutput] = Queue()
        self.microbatch_watch_thread = Thread(
            target=self._microbatch_watch_loop, daemon=True
        )
        self.output_thread = Thread(target=self._output_loop, daemon=True)
        self.microbatch_output_processing_sync_queue: Queue[Any] = Queue()

        self.pending_step_outputs: List[Tuple[SchedulerOutput, SamplerOutputs]] = []

    def _init_zmq_sockets(self):
        super()._init_zmq_sockets()
        # PULL socket for microbatch completion signal
        self.microbatch_socket = self.zmq_context.socket(zmq.PULL)
        self._bind_zmq_socket(
            self.microbatch_socket, self.comm_info.microbatch_socket_port
        )

    def _validate_parallel_config(self) -> None:
        assert self.config.parallel_config.pipeline_parallel_size > 1

    def start_controller_execution(self) -> None:
        """Starts the execution loop."""
        self.has_started_execution_loops = True
        self.schedule_event.set()
        self.schedule_thread.start()
        self.output_thread.start()
        self.scheduler_timer_thread.start()
        self.microbatch_watch_thread.start()
        logger.info(
            f"Started for replica id {self.replica_id}:\n"
            "  1. Scheduler timer thread\n"
            "  2. Schedule thread\n"
            "  3. Output thread\n"
            "  4. Microbatch watch thread"
        )

    def _get_worker_impl(self):
        # Lazy import the Worker to avoid importing torch.cuda/xformers
        # before CUDA_VISIBLE_DEVICES is set in the Worker
        from vajra.worker.pipeline_parallel_llm_worker import PipelineParallelWorker

        return PipelineParallelWorker

    @synchronized
    def _append_pending_step_output(
        self, scheduler_output: SchedulerOutput, sampler_outputs: SamplerOutputs
    ) -> None:
        self.pending_step_outputs.append((scheduler_output, sampler_outputs))

    @synchronized
    def _get_pending_step_outputs(
        self,
    ) -> List[Tuple[SchedulerOutput, SamplerOutputs]]:
        pending_step_outputs = self.pending_step_outputs
        self.pending_step_outputs = []
        return pending_step_outputs

    @exit_on_error
    def _schedule_loop(self) -> NoReturn:
        while True:
            self.schedule_event.wait()
            self.schedule_event.clear()

            start_time = time.time()
            scheduler_output = self.scheduler.schedule()

            if scheduler_output.has_no_output:
                continue

            ignored_seqs, seqs = self.seq_manager.on_schedule(scheduler_output)

            self.scheduler_output_queue.put(
                ScheduleStageOutputs(
                    ignored_seqs,
                    seqs,
                    scheduler_output,
                    start_time,
                )
            )

            end_time = time.time()

            if not scheduler_output.is_empty:
                self.microbatch_watch_queue.put(scheduler_output)
                step_inputs = StepInputs(
                    scheduler_output,
                    new_seq_params=self._get_new_seq_params(),
                    pending_step_outputs=self._get_pending_step_outputs(),
                )
                ZMQHelper.send_pyobj(self.enqueue_socket, step_inputs)

            self.metrics_store.on_schedule(scheduler_output, start_time, end_time)

    @exit_on_error
    def _microbatch_watch_loop(self) -> None:
        pending_microbatch_outputs: Dict[int, List[StepMicrobatchOutputs]] = (
            defaultdict(list)
        )

        while True:
            scheduler_output = self.microbatch_watch_queue.get()
            schedule_id = scheduler_output.id
            num_microbatch_outputs_received = 0

            num_microbatch_outputs_received += len(
                pending_microbatch_outputs[schedule_id]
            )
            del pending_microbatch_outputs[schedule_id]

            while (
                num_microbatch_outputs_received
                < self.config.parallel_config.kv_parallel_size
            ):
                step_microbatch_outputs = ZMQHelper.recv_pyobj(
                    self.microbatch_socket, StepMicrobatchOutputsProto
                )
                if step_microbatch_outputs.schedule_id != schedule_id:
                    pending_microbatch_outputs[
                        step_microbatch_outputs.schedule_id
                    ].append(step_microbatch_outputs)
                    continue

                num_microbatch_outputs_received += 1

            self.seq_manager.on_stage_completed(scheduler_output)
            self.scheduler.on_stage_completed(
                [
                    self.seq_manager.get_seq(s.seq_id)
                    for s in scheduler_output.seq_schedule_metadata_list
                ]
            )
            self.microbatch_output_processing_sync_queue.put(None)
            self.schedule_event.set()

    @exit_on_error
    def _output_loop(self) -> None:
        pending_sampler_outputs: Dict[int, List[SamplerOutputs]] = defaultdict(list)

        while True:
            scheduler_stage_output = self.scheduler_output_queue.get()
            schedule_id = scheduler_stage_output.scheduler_output.id
            num_step_outputs_received = 0

            all_sampler_outputs: List[SamplerOutputs] = []
            all_sampler_outputs.extend(pending_sampler_outputs[schedule_id])
            num_step_outputs_received += len(pending_sampler_outputs[schedule_id])
            del pending_sampler_outputs[schedule_id]

            while (
                num_step_outputs_received < self.config.parallel_config.kv_parallel_size
            ):
                step_output = ZMQHelper.recv_pyobj(self.output_socket, StepOutputsProto)
                if step_output.schedule_id != schedule_id:
                    pending_sampler_outputs[step_output.schedule_id].append(
                        step_output.sampler_outputs
                    )
                    continue
                all_sampler_outputs.append(step_output.sampler_outputs)
                num_step_outputs_received += 1

            combined_sampler_outputs = self._combine_sampler_outputs(
                all_sampler_outputs,
                scheduler_stage_output.scheduler_output.seq_schedule_metadata_list,
            )

            self._append_pending_step_output(
                scheduler_stage_output.scheduler_output, combined_sampler_outputs
            )

            self.microbatch_output_processing_sync_queue.get()
            all_request_outputs = self._on_step_completed(
                scheduler_stage_output.scheduler_output,
                scheduler_stage_output.ignored_seqs,
                scheduler_stage_output.seqs,
                combined_sampler_outputs,
                scheduler_stage_output.start_time,
            )
            self.global_output_queue.put(all_request_outputs)
            self.schedule_event.set()
            self.output_queue.put(all_request_outputs)

    def add_request(
        self,
        prompt: str,
        sampling_params: SamplingParams,
        prompt_token_ids: Optional[List[int]] = None,
        seq_id: Optional[str] = None,
    ) -> None:
        raise NotImplementedError(
            "add_request is not implemented for PipelineParallelLLMReplicaController"
        )

    def step(self, block: bool = False) -> List[RequestOutput]:
        """Performs one decoding iteration and returns newly generated results.

        This function performs one decoding iteration of the engine.
        This version does everything asynchronously and returns the results
        """
        if not self.has_started_execution_loops:
            self.start_controller_execution()

        if block:
            return self.output_queue.get()

        try:
            return self.output_queue.get(block=False)
        except Empty:
            return []
