import os
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

import torch
import wandb

from vajra._native.metrics_store import ChromeTracer  # type: ignore
from vajra._native.metrics_store import (
    Metric,
    MetricType,
    get_all_metrics,
    get_completion_time_series_metrics_types,
    get_cpu_operation_metrics_types,
    get_gpu_operation_metrics_types,
)
from vajra.config import BaseReplicaControllerConfig
from vajra.datatypes import SchedulerOutput  # type: ignore
from vajra.datatypes import Sequence  # type: ignore
from vajra.datatypes import SequenceMetadata  # type: ignore
from vajra.logger import init_logger

from .datastores.base_cdf_datastore import BaseCDFDataStore
from .datastores.base_datastore import BaseDataStore
from .datastores.datastore_factory import DataStoreFactory
from .datastores.time_series_datastore import TimeSeriesDataStore
from .plotter import Plotter

logger = init_logger(__name__)


def if_write_metrics(func):

    def wrapper(self, *args, **kwargs):
        if self.config.write_metrics and self.initial_memory_profiling_done:
            return func(self, *args, **kwargs)

    return wrapper


def check_enabled(func):

    def wrapper(self, *args, **kwargs):
        if self.disabled:
            return
        return func(self, *args, **kwargs)

    return wrapper


PROFILE_LAYER_ID = 1


class MetricsStore:
    _instance: Optional["MetricsStore"] = None

    def __init__(
        self,
        replica_id: int,
        replica_controller_config: BaseReplicaControllerConfig,
        output_dir: Optional[str] = None,
    ):
        self.disabled = False

        self.config = replica_controller_config.metrics_config
        self.replica_id = replica_id
        self.output_dir = output_dir or "."
        self.initial_memory_profiling_done = False
        self.model_num_layers = (
            replica_controller_config.model_config.get_total_num_layers()
        )

        if not self.config or not self.config.write_metrics:
            logger.info("MetricsStore disabled")
            self.disabled = True
            return

        self.plots_dir = f"{self.output_dir}/plots/"
        os.makedirs(self.plots_dir, exist_ok=True)

        self.metrics: Dict[MetricType, Metric] = get_all_metrics(
            self.config.write_metrics,
            self.config.keep_individual_batch_metrics,
            self.config.enable_gpu_op_level_metrics,
            self.config.enable_cpu_op_level_metrics,
        )
        self.gpu_op_metrics_types = get_gpu_operation_metrics_types()
        self.cpu_op_metrics_types = get_cpu_operation_metrics_types()

        self.reset()
        self._init_wandb()

    @classmethod
    def get_or_create_instance(
        cls,
        replica_id: int,
        replica_controller_config: BaseReplicaControllerConfig,
        output_dir: str,
    ):
        cls._instance = cls(replica_id, replica_controller_config, output_dir)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "MetricsStore":
        assert cls._instance is not None, "MetricsStore not initialized"
        return cls._instance

    def is_op_enabled(
        self,
        metric_type: MetricType,
        rank: Optional[int] = None,
        layer_id: Optional[int] = None,
    ) -> bool:
        if self.disabled:
            return False

        if metric_type in self.gpu_op_metrics_types:
            return self.config.enable_gpu_op_level_metrics and (
                layer_id == PROFILE_LAYER_ID or layer_id is None
            )
        elif metric_type in self.cpu_op_metrics_types:
            if not self.config.enable_cpu_op_level_metrics:
                return False
            return rank == 0
        raise ValueError(f"Unknown metric name: {metric_type}")

    def reset(self):
        if self.disabled:
            return

        self.datastores: Dict[MetricType, BaseDataStore] = {
            metric.type: DataStoreFactory.get_datastore(
                metric, self.plots_dir, self.config.store_png
            )
            for metric in self.metrics
        }
        # temporary storage for cuda events
        self.gpu_ops_metrics_pending_cuda_events: Dict[
            MetricType, List[Tuple[torch.cuda.Event, torch.cuda.Event]]
        ] = {metric_type: [] for metric_type in self.gpu_op_metrics_types}
        for metric_type in self.gpu_op_metrics_types:
            if not metric_type in self.datastores:
                continue
            datastore = self.datastores[metric_type]
            assert isinstance(datastore, BaseCDFDataStore)
            datastore.set_value_multiplier(self.model_num_layers)

        self.chrome_tracer = ChromeTracer(self.replica_id, self.output_dir)
        # to measure the time interval between the last request and the next request
        self.last_request_arrived_at = None
        # to measure the time wasted between the last batch and the next batch
        self.last_batch_end_time = None
        self.num_decoded_tokens = 0
        # This is used to associate op metrics with the correct scheduler output
        self.scheduler_output_id = None

    def _init_wandb(self):
        if (
            not self.config.write_metrics
            or not self.config.wandb_project
            or not self.config.wandb_group
        ):
            return

        logger.info(
            f"Initializing wandb with project: {self.config.wandb_project}, group: {self.config.wandb_group}, run_name: {self.config.wandb_run_name}"
            f", sweep_id: {self.config.wandb_sweep_id}, run_id: {self.config.wandb_run_id}"
        )
        if self.config.wandb_sweep_id or self.config.wandb_run_id:
            logger.warn("wandb_sweep_id and wandb_run_id are not supported yet.")

        wandb.init(
            project=self.config.wandb_project,
            group=self.config.wandb_group,
            name=self.config.wandb_run_name,
        )

    def get_config_for_worker(self):
        config = deepcopy(self.config)
        config.wandb_project = None
        config.wandb_group = None

        return config

    @check_enabled
    def mark_initial_memory_profiling_done(self):
        self.initial_memory_profiling_done = True

    @check_enabled
    @if_write_metrics
    def on_request_arrival(self, seq: Sequence) -> None:
        self.datastores[MetricType.REQUEST_ARRIVED].put(seq.state.arrived_at, 1)
        if self.last_request_arrived_at is not None:
            self.datastores[MetricType.REQUEST_INTER_ARRIVAL_DELAY].put(
                seq.seq_id,
                seq.state.arrived_at - self.last_request_arrived_at,
            )
        self.last_request_arrived_at = seq.state.arrived_at

    @if_write_metrics
    def _on_request_end(self, seq: Sequence) -> None:
        assert seq.is_finished()
        assert seq.state.is_completed

        # log request outputs and completion metrics regardless of whether the request is ignored or not
        self.datastores[MetricType.REQUEST_COMPLETED].put(seq.state.completed_at, 1)
        self.datastores[MetricType.REQUEST_NUM_IGNORED].put(
            seq.seq_id, int(seq.state.is_ignore_finished)
        )

        if seq.state.is_ignore_finished:
            # do not log metrics for ignored requests, they can skew the results
            return

        # first log all the histograms
        self.datastores[MetricType.REQUEST_NUM_TOKENS].put(
            seq.seq_id, seq.state.num_total_tokens
        )
        self.datastores[MetricType.REQUEST_PREFILL_TOKENS].put(
            seq.seq_id, seq.state.num_prompt_tokens
        )
        self.datastores[MetricType.REQUEST_DECODE_TOKENS].put(
            seq.seq_id, seq.state.num_output_tokens
        )
        self.datastores[MetricType.REQUEST_PD_RATIO].put(
            seq.seq_id,
            seq.state.num_prompt_tokens / seq.state.num_output_tokens,
        )
        self.datastores[MetricType.REQUEST_NUM_RESTARTS].put(
            seq.seq_id, seq.state.num_restarts
        )
        self.datastores[MetricType.REQUEST_NUM_PAUSES].put(
            seq.seq_id, seq.state.num_pauses
        )

        # then log all the time distributions
        self.datastores[MetricType.REQUEST_E2E_TIME].put(seq.seq_id, seq.state.e2e_time)
        self.datastores[MetricType.REQUEST_E2E_TIME_NORMALIZED].put(
            seq.seq_id, seq.state.e2e_time_normalized
        )
        self.datastores[MetricType.REQUEST_E2E_TIME_PIECEWISE_NORMALIZED].put(
            seq.seq_id, seq.state.e2e_time_piecewise_normalized
        )
        self.datastores[MetricType.REQUEST_EXECUTION_PLUS_PREEMPTION_TIME].put(
            seq.seq_id,
            seq.state.execution_plus_preemption_time,
        )
        self.datastores[
            MetricType.REQUEST_EXECUTION_PLUS_PREEMPTION_TIME_NORMALIZED
        ].put(
            seq.seq_id,
            seq.state.execution_plus_preemption_time_normalized,
        )
        assert seq.state.scheduling_delay is not None
        self.datastores[MetricType.REQUEST_SCHEDULING_DELAY].put(
            seq.seq_id,
            seq.state.scheduling_delay,
        )
        self.datastores[MetricType.REQUEST_EXECUTION_TIME].put(
            seq.seq_id, seq.state.execution_time
        )
        self.datastores[MetricType.REQUEST_EXECUTION_TIME_NORMALIZED].put(
            seq.seq_id, seq.state.execution_time_normalized
        )
        self.datastores[MetricType.REQUEST_PREEMPTION_TIME].put(
            seq.seq_id, seq.state.preempted_time
        )
        assert seq.state.e2e_prefill_time is not None
        self.datastores[MetricType.PREFILL_TIME_E2E].put(
            seq.seq_id, seq.state.e2e_prefill_time
        )
        assert seq.state.e2e_prefill_time_normalized is not None
        self.datastores[MetricType.PREFILL_TIME_E2E_NORMALIZED].put(
            seq.seq_id, seq.state.e2e_prefill_time_normalized
        )
        assert seq.state.e2e_prefill_time_piecewise_normalized is not None
        self.datastores[MetricType.PREFILL_TIME_E2E_PIECEWISE_NORMALIZED].put(
            seq.seq_id,
            seq.state.e2e_prefill_time_piecewise_normalized,
        )
        self.datastores[MetricType.PREFILL_TIME_EXECUTION_PLUS_PREEMPTION].put(
            seq.seq_id,
            seq.state.prefill_execution_plus_preemption_time,
        )
        assert seq.state.prefill_execution_plus_preemption_time_normalized is not None
        self.datastores[
            MetricType.PREFILL_TIME_EXECUTION_PLUS_PREEMPTION_NORMALIZED
        ].put(
            seq.seq_id,
            seq.state.prefill_execution_plus_preemption_time_normalized,
        )
        assert seq.state.decode_execution_plus_preemption_time_normalized is not None
        self.datastores[
            MetricType.DECODE_TIME_EXECUTION_PLUS_PREEMPTION_NORMALIZED
        ].put(
            seq.seq_id,
            seq.state.decode_execution_plus_preemption_time_normalized,
        )

    def _update_per_token_execution_times(
        self,
        batch_end_time: float,
        seq: Sequence,
    ) -> None:
        # determine if this was prefill or decode token
        if not seq.prompt_processing_finished:
            return

        self.num_decoded_tokens += 1

        # if prefill has just finished in this iteration, update the prefill completion timeseries
        if seq.output_len == 1:
            self.datastores[MetricType.PREFILL_COMPLETED].put(
                batch_end_time,
                seq.state.num_prompt_tokens,
            )

        self.datastores[MetricType.DECODE_TOKEN_EXECUTION_PLUS_PREEMPTION_TIME].put(
            self.num_decoded_tokens,
            seq.state.last_token_generation_time,
        )

        if self.config.keep_individual_batch_metrics:
            self.datastores[MetricType.DECODE_COMPLETED].put(batch_end_time, 1)

    @check_enabled
    @if_write_metrics
    def on_schedule(
        self,
        scheduler_output: SchedulerOutput,
        start_time: float,
        end_time: float,
    ) -> None:
        # NOTE: This is called on the engine
        self.scheduler_output_id = scheduler_output.id

        if not self.config.enable_chrome_trace:
            return

        # Use the dedicated method for logging scheduler events
        self.chrome_tracer.put_scheduler_event(
            scheduler_output.id,
            scheduler_output.seq_schedule_metadata_list,
            start_time,
            end_time,
        )

    @check_enabled
    @if_write_metrics
    def on_batch_stage_start(
        self,
        scheduler_output: SchedulerOutput,
    ):
        # NOTE: This is called on the worker
        self.scheduler_output_id = scheduler_output.id

    @check_enabled
    @if_write_metrics
    def on_batch_stage_end(
        self,
        seq_metadata_list: List[SequenceMetadata],
        tensor_parallel_rank: int,
        pipeline_parallel_rank: int,
        kv_parallel_rank: int,
        start_time: float,
        end_time: float,
    ) -> None:
        # NOTE: This is called on the worker
        self._process_pending_operation_metrics_events()

        if not self.config.enable_chrome_trace:
            return

        self.chrome_tracer.put(
            seq_metadata_list,
            tensor_parallel_rank,
            pipeline_parallel_rank,
            kv_parallel_rank,
            start_time,
            end_time,
        )

    @check_enabled
    @if_write_metrics
    def on_batch_end(
        self,
        seqs: List[Sequence],
        scheduler_output: SchedulerOutput,
        batch_start_time: float,
        batch_end_time: float,
    ) -> None:
        # NOTE: This is called on the engine
        execution_time = batch_end_time - batch_start_time

        for seq in seqs:
            self._update_per_token_execution_times(batch_end_time, seq)
            if seq.is_finished():
                self._on_request_end(seq)

        if self.last_batch_end_time is not None:
            self.datastores[MetricType.INTER_BATCH_DELAY].put(
                scheduler_output.id,
                batch_start_time - self.last_batch_end_time,
            )
        self.last_batch_end_time = batch_end_time

        num_tokens = sum(
            [s.num_q_tokens for s in scheduler_output.seq_schedule_metadata_list]
        )
        num_prompt_tokens = sum(
            [
                s.num_q_tokens
                for s in scheduler_output.seq_schedule_metadata_list
                if s.num_q_tokens > 1
            ]
        )
        num_output_tokens = num_tokens - num_prompt_tokens

        self.datastores[MetricType.BATCH_NUM_TOKENS].put(
            scheduler_output.id,
            num_tokens,
        )
        self.datastores[MetricType.BATCH_NUM_PREFILL_TOKENS].put(
            scheduler_output.id, num_prompt_tokens
        )
        self.datastores[MetricType.BATCH_NUM_DECODE_TOKENS].put(
            scheduler_output.id, num_output_tokens
        )

        self.datastores[MetricType.BATCH_SIZE].put(scheduler_output.id, len(seqs))
        # add the only time distribution we have for batch
        self.datastores[MetricType.BATCH_EXECUTION_TIME].put(
            scheduler_output.id, execution_time
        )

    def _process_pending_operation_metrics_events(self):
        for metric_type, events in self.gpu_ops_metrics_pending_cuda_events.items():
            for event in events:
                start_event, end_event = event
                time = start_event.elapsed_time(end_event)
                self.push_operation_metrics(metric_type, time)
            self.gpu_ops_metrics_pending_cuda_events[metric_type] = []

    @check_enabled
    @if_write_metrics
    def push_operation_metrics_events(
        self,
        metric_type: MetricType,
        start_event: torch.cuda.Event,
        end_event: torch.cuda.Event,
    ):
        if not self.config.enable_gpu_op_level_metrics:
            return

        self.gpu_ops_metrics_pending_cuda_events[metric_type].append(
            (start_event, end_event)
        )

    @check_enabled
    @if_write_metrics
    def push_operation_metrics(
        self,
        metric_type: MetricType,
        time: float,
    ):
        if not self.config.enable_gpu_op_level_metrics:
            return
        self.datastores[metric_type].put(self.scheduler_output_id, time)

    @check_enabled
    @if_write_metrics
    def push_cpu_operation_metrics(
        self,
        metric_type: MetricType,
        time: float,
    ):
        if not self.config.enable_cpu_op_level_metrics:
            return
        self.datastores[metric_type].put(self.scheduler_output_id, time)

    @check_enabled
    @if_write_metrics
    def plot(self):
        if self.disabled:
            return

        start_time = self.datastores[MetricType.REQUEST_ARRIVED].start_time  # type: ignore
        if start_time is None:
            logger.warning("No metrics to plot")
            return

        # Set time offset for all time series datastores
        for metric_type in get_completion_time_series_metrics_types():
            datastore = self.datastores[metric_type]
            assert isinstance(datastore, TimeSeriesDataStore)
            datastore.set_time_offset(start_time)

        for datastore in self.datastores.values():
            datastore.plot()

        Plotter.store_associated_metrics(self.datastores, self.output_dir)
        Plotter.store_comparison_metrics(
            self.datastores, self.plots_dir, self.config.store_png
        )

        self.chrome_tracer.store()

    @check_enabled
    def merge(self, other: "MetricsStore"):
        for metric_type, datastore in self.datastores.items():
            datastore.merge(other.datastores[metric_type])
        self.chrome_tracer.merge(other.chrome_tracer)
