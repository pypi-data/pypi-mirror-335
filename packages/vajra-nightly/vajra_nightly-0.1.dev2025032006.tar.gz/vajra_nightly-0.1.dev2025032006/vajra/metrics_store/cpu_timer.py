from time import perf_counter
from typing import Optional

import torch

from vajra._native.metrics_store import MetricType

from .metrics_store import MetricsStore


class CpuTimer:

    def __init__(self, metric_type: MetricType, rank: Optional[int] = None):
        self.metric_type = metric_type
        self.start_time: float = 0
        self.metrics_store = MetricsStore.get_instance()
        self.disabled = not self.metrics_store.is_op_enabled(
            metric_type=self.metric_type, rank=rank
        )

    def __enter__(self):
        if self.disabled:
            return

        self.start_time = perf_counter()
        return self

    def __exit__(self, *_):
        if self.disabled:
            return

        torch.cuda.synchronize()
        self.metrics_store.push_cpu_operation_metrics(
            self.metric_type, (perf_counter() - self.start_time) * 1e3  # convert to ms
        )
