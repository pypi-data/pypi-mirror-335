# type: ignore
# torch.cuda.Event has weird typing, so we need to ignore it
from typing import Optional

import torch

from vajra._native.metrics_store import CudaTimer as CudaTimerC
from vajra._native.metrics_store import MetricType

from .metrics_store_handle import MetricsStoreHandle

USE_CUDA_EVENTS = True


class CudaTimer:

    def __init__(
        self,
        metric_type: Optional[MetricType],
        layer_id: Optional[int] = None,
        rank: Optional[int] = None,
    ):
        self.metrics_store = MetricsStoreHandle.get_instance()
        self.native_handle = CudaTimerC(
            metric_type, self.metrics_store.native_handle, layer_id, rank
        )
        self.disabled = (
            metric_type is None
            or not self.metrics_store.is_operation_enabled(metric_type, layer_id, rank)
        )

        if self.disabled:
            return

        self.profiler = torch.profiler.profile(
            activities=[torch.profiler.ProfilerActivity.CUDA],
            on_trace_ready=self.handle_trace,
        )

    def __enter__(self):
        if self.disabled:
            return

        if USE_CUDA_EVENTS:
            self.native_handle.start()
        else:
            self.profiler.__enter__()

        return self

    def handle_trace(self, trace):
        assert self.metrics_store is not None

        total_cuda_time = sum([e.cuda_time_total for e in trace.key_averages()])

        self.metrics_store.push_gpu_operation_metric(
            self.metrics_store,
            total_cuda_time * 1e-3,  # convert to ms
        )

    def __exit__(self, *args):
        if self.disabled:
            return

        assert self.metrics_store is not None

        if USE_CUDA_EVENTS:
            self.native_handle.stop()
        else:
            self.profiler.__exit__(*args)
