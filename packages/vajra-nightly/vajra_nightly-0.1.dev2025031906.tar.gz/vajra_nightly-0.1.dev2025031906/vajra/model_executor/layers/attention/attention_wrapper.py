from typing import Dict, List, Tuple

import torch

from vajra._native.model_executor import SequenceArrangement as SequenceArrangementC
from vajra.config import ModelConfig, ParallelConfig, WorkerConfig
from vajra.datatypes import SequenceMetadata  # type: ignore
from vajra.logger import init_logger
from vajra.metrics_store import CudaTimer, MetricType  # type: ignore
from vajra.model_executor.layers.attention.flashinfer_attention_wrapper import (
    FlashinferAttentionWrapper,
)
from vajra.model_executor.layers.attention.sequence_arrangement import (
    SequenceArrangement,
)

logger = init_logger(__name__)


class AttentionWrapper:
    _inst = None

    def __init__(
        self,
        model_config: ModelConfig,
        parallel_config: ParallelConfig,
        worker_config: WorkerConfig,
        block_size: int,
        device: torch.device,
    ):
        self.device = device
        self.num_q_heads = model_config.get_num_q_heads(parallel_config)
        self.num_kv_heads = model_config.get_num_kv_heads(parallel_config)
        self.head_dim = model_config.get_head_size()
        self.dtype = model_config.torch_dtype
        self.block_size = block_size
        self.use_native_execution_backend: bool = (
            worker_config.use_native_execution_backend
        )

        self.is_metadata_initialized = False
        self.is_profiling_iteration = False

        num_sequence_splits = SequenceArrangement.get_num_splits()

        logger.info(
            f"Creating {num_sequence_splits} FlashinferAttentionWrapper instances."
        )

        self.wrappers = [
            FlashinferAttentionWrapper(
                self.num_q_heads,
                self.num_kv_heads,
                self.head_dim,
                self.block_size,
                self.use_native_execution_backend,
                device,
            )
            for _ in range(num_sequence_splits)
        ]

        self.timers: Dict[Tuple[MetricType, int], CudaTimer] = {}

    def get_timer(self, metric: MetricType, layer_id: int) -> CudaTimer:
        key = (metric, layer_id)

        if key not in self.timers:
            self.timers[key] = CudaTimer(*key)

        return self.timers.get(key)  # type: ignore

    def begin_forward(
        self,
        seq_metadata_list: List[SequenceMetadata],
    ) -> None:
        assert not self.is_metadata_initialized
        self.is_metadata_initialized = True
        self.is_profiling_iteration = False

        if not seq_metadata_list or not seq_metadata_list[0].block_table:
            self.is_profiling_iteration = True
            return

        if self.use_native_execution_backend:
            seq_arrangement = SequenceArrangementC()
        else:
            seq_arrangement = SequenceArrangement()

        seq_arrangement.check_arrangement_and_extend(seq_metadata_list)
        split_seq_metadata_list = seq_arrangement.get_splits()

        for s, wrapper in zip(split_seq_metadata_list, self.wrappers):
            wrapper.begin_forward(s)

    def end_forward(self):
        assert self.is_metadata_initialized
        self.is_metadata_initialized = False

        if self.is_profiling_iteration:
            return

        for wrapper in self.wrappers:
            wrapper.end_forward()

    @classmethod
    def get_instance(cls):
        assert (
            cls._inst is not None
        ), "Instance not created. Call create_instance() first."
        return cls._inst

    @classmethod
    def create_instance(cls, *args, **kwargs):
        cls._inst = cls(*args, **kwargs)
        return cls._inst

    def get_cache_block(self, num_blocks: int) -> torch.Tensor:
        return torch.randn(
            num_blocks,
            2,
            self.block_size,
            self.num_kv_heads,
            self.head_dim,
            dtype=self.dtype,
            device=self.device,
        )

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        kv_cache: torch.Tensor,
        layer_id: int,
    ) -> torch.Tensor:
        assert self.is_metadata_initialized

        if self.is_profiling_iteration:
            return torch.empty_like(query)

        output = torch.empty(
            query.shape[0],
            self.num_q_heads,
            self.head_dim,
            dtype=query.dtype,
            device=query.device,
        )

        logsumexp = torch.empty(
            query.shape[0],
            self.num_q_heads,
            dtype=torch.float32,
            device=query.device,
        )

        with self.get_timer(MetricType.ATTN_INPUT_RESHAPE, layer_id):
            query = query.reshape(-1, self.num_q_heads, self.head_dim)
            key = key.reshape(-1, self.num_kv_heads, self.head_dim)
            value = value.reshape(-1, self.num_kv_heads, self.head_dim)

        with self.get_timer(MetricType.ATTN_KV_CACHE_SAVE, layer_id):
            q_offset = 0
            for wrapper in self.wrappers:
                q_len = wrapper.get_num_q_tokens()

                if q_len == 0:
                    continue

                wrapper.save_kv_cache(
                    key[q_offset : q_offset + q_len],
                    value[q_offset : q_offset + q_len],
                    kv_cache,
                )
                q_offset += q_len

        with self.get_timer(MetricType.ATTN, layer_id):
            q_offset = 0
            for wrapper in self.wrappers:
                q_len = wrapper.get_num_q_tokens()

                if q_len == 0:
                    continue

                wrapper.run(
                    query[q_offset : q_offset + q_len],
                    output[q_offset : q_offset + q_len],
                    logsumexp[q_offset : q_offset + q_len],
                    kv_cache,
                )
                q_offset += q_len

        with self.get_timer(MetricType.ATTN_OUTPUT_RESHAPE, layer_id):
            output = output.reshape(-1, self.num_q_heads * self.head_dim)

        return output
