from typing import Optional

import torch
import torch.distributed
import zmq

from vajra.datatypes import SamplerOutputs  # type: ignore
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import (
    StepInputs,
    StepMicrobatchOutputs,
    StepOutputs,
)
from vajra.datatypes.generated.worker_protocol_pb2 import (
    StepInputs as StepInputsProto,  # type: ignore
)
from vajra.logger import init_logger
from vajra.utils.threading_utils import exit_on_error
from vajra.utils.zmq_helper import ZMQHelper
from vajra.worker.base_llm_worker import BaseLLMWorker

logger = init_logger(__name__)


class PipelineParallelWorker(BaseLLMWorker):
    """A worker class that executes (a partition of) the model on a GPU.

    Each worker is associated with a single GPU. The worker is responsible for
    maintaining the KV cache and executing the model on the GPU. In case of
    distributed inference, each worker is assigned a partition of the model.
    """

    def _init_zmq_sockets(self):
        super()._init_zmq_sockets()

        self.microbatch_socket = self.zmq_context.socket(zmq.PUSH)
        self.microbatch_socket.connect(
            f"tcp://{self.comm_info.engine_ip_address}:{self.comm_info.microbatch_socket_port}"
        )

    def _verify_parallel_config(self) -> None:
        assert self.config.parallel_config.pipeline_parallel_size > 1

    def on_step_completed(
        self,
        scheduler_output: SchedulerOutput,
        sampler_outputs: Optional[SamplerOutputs],
    ) -> None:
        assert self.seq_manager
        # in pipeline parallel case, each stage won't have sampler output
        # so we need to do the book keeping update later, here we just want to update the stuff for
        # this stage completion
        self.seq_manager.on_stage_completed(scheduler_output)

    @exit_on_error
    def _execution_loop(self) -> None:
        assert self.seq_manager

        torch.cuda.set_device(self.device)

        self.worker_ready_event.set()

        while True:
            step_inputs: StepInputs = ZMQHelper.recv_pyobj(
                self.enqueue_socket, StepInputsProto
            )

            for params in step_inputs.new_seq_params:  # type: ignore
                new_seq = Sequence(params)
                self.seq_manager.add_seq(new_seq)

            for pending_step_output in step_inputs.pending_step_outputs:  # type: ignore
                self.seq_manager.on_step_completed(
                    pending_step_output[
                        0
                    ].seq_schedule_metadata_list,  # scheduler_output
                    pending_step_output[1],  # sampler_outputs
                )

            output = self.execute_model(step_inputs.scheduler_output)

            if not self.is_tensor_parallel_rank_zero:
                continue

            if self.is_last_pipeline_stage:
                assert output

                logger.debug(
                    f"Worker {self.rank} sending output to engine: {output} for {step_inputs.scheduler_output}",
                )
                step_outputs = StepOutputs(
                    step_inputs.scheduler_output.id,
                    output,
                )
                ZMQHelper.send_pyobj(self.output_socket, step_outputs)
            elif self.is_first_pipeline_stage:
                logger.debug(
                    f"Worker {self.rank} sending microbatch signal for {step_inputs.scheduler_output}",
                )
                step_microbatch_outputs = StepMicrobatchOutputs(
                    step_inputs.scheduler_output.id
                )
                ZMQHelper.send_pyobj(self.microbatch_socket, step_microbatch_outputs)
