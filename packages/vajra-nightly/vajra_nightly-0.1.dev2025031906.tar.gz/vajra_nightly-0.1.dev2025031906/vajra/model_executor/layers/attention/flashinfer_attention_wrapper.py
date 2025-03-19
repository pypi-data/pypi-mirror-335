from typing import List

import torch
import torch.distributed
from flashinfer import BatchPrefillWithPagedKVCacheWrapper

from vajra._kernels import reshape_and_cache_flashinfer
from vajra._native.model_executor import (
    FlashinferAttentionWrapper as FlashinferAttentionWrapperC,  # type: ignore
)
from vajra.datatypes import SequenceMetadata  # type: ignore

# 128 MB workspace buffer as per the flashinfer documentation
FLASHINFER_WORKSPACE_SIZE = 128 * 1024 * 1024


def check_metadata_initialized(func):
    def wrapper(self, *args, **kwargs):
        assert self.is_metadata_initialized, "Metadata is not initialized."
        return func(self, *args, **kwargs)

    return wrapper


class FlashinferAttentionWrapper:
    def __init__(
        self,
        num_q_heads: int,
        num_kv_heads: int,
        head_dim: int,
        block_size: int,
        use_native_execution_backend: bool,
        device: torch.device,
    ):
        self.num_q_heads = num_q_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = head_dim
        self.block_size = block_size
        self.use_native_execution_backend = use_native_execution_backend
        self.device = device

        self.is_metadata_initialized = False
        self.is_no_op = False
        self.should_save_kv_cache = False
        self.num_q_tokens = 0

        # Initialize native handle during init if using native backend
        if self.use_native_execution_backend:
            self.native_handle = FlashinferAttentionWrapperC(
                self.num_q_heads,
                self.num_kv_heads,
                self.head_dim,
                self.block_size,
                self.device,
            )
            self.wrapper = None
        else:
            self.native_handle = None
            workspace_buffer = torch.empty(
                FLASHINFER_WORKSPACE_SIZE, dtype=torch.uint8, device=device
            )
            self.wrapper = BatchPrefillWithPagedKVCacheWrapper(workspace_buffer)

    def _to_int_tensor(self, data: List[int]) -> torch.Tensor:
        return torch.tensor(data, dtype=torch.int32, device=self.device)

    def _to_long_tensor(self, data: List[int]) -> torch.Tensor:
        return torch.tensor(data, dtype=torch.int64, device=self.device)

    def begin_forward(
        self,
        seq_metadata_list: List[SequenceMetadata],
    ) -> None:
        # The indptr tensor captures the location query tokens in the input tensor.
        # Flashinfer calls this layout as a raggedtensor. The indptr tensor captures the start of each
        # sequence in the ragged tensor. The length of the indptr tensor is the number of sequences + 1.
        # We perform both prefill and decode attention in a single call to batched prefill kernel.
        assert not self.is_metadata_initialized
        self.is_metadata_initialized = True

        self.is_no_op = len(seq_metadata_list) == 0
        self.num_q_tokens = 0

        if self.use_native_execution_backend:
            assert self.native_handle is not None

            # Process metadata in C++
            self.native_handle.begin_forward(seq_metadata_list)

            if self.is_no_op:
                return

            # Get state from native handle
            self.num_q_tokens = self.native_handle.num_q_tokens
            self.should_save_kv_cache = self.native_handle.should_save_kv_cache

            if self.should_save_kv_cache:
                self.slot_mapping_tensor = self.native_handle.slot_mapping_tensor
            return

        # Python implementation
        if self.is_no_op:
            return

        qo_indptr: List[int] = [0]
        # The kv_page_indices tensor captures the pages of the key-value cache that
        # are assigned to each token in the input tensor. Since there is a variable number
        # of pages assigned to each sequence, a ragged tensor to represent this.
        kv_page_indices: List[int] = []
        # the last page might not be full, so we need to keep track of the length of the last page
        kv_last_page_len: List[int] = []
        # Since the prefill_kv_page_indices tensor is a ragged tensor, we also need to keep track of the
        # indptr tensor for the prefill_kv_page_indices tensor. This tensor captures the start of each sequence
        # in the ragged tensor.
        kv_page_indptr: List[int] = [0]

        # We need to maintain additional metadata for KVP sequences.
        # This is metadata is required to perform the online softmax reduction operation
        self.kvp_seqs_offset: int = 0
        self.kvp_seqs_qo_indptr: List[int] = [0]
        self.kvp_seqs_group_ids: List[List[int]] = []

        slot_mapping: List[int] = []

        # In kvp seqs, sometimes, we might not want to save the KV cache.
        # When this is true, we can't perform causal attention. So, we can either
        # execute requests which all require saving KV cache or none of them.
        seqs_save_kv_cache: List[bool] = [
            seq_metadata.save_kv_cache for seq_metadata in seq_metadata_list
        ]
        all_save_kv_cache: bool = all(seqs_save_kv_cache)
        none_save_kv_cache: bool = not any(seqs_save_kv_cache)
        assert (
            all_save_kv_cache or none_save_kv_cache
        ), "All KVP sequences should either save KV cache or not save KV cache."
        self.should_save_kv_cache: bool = all_save_kv_cache

        # The sequences are sorted as
        # | non kvp seqs | kvp seqs |
        started_kvp_seqs = False

        for seq_metadata in seq_metadata_list:
            num_q_tokens = seq_metadata.num_q_tokens
            num_kv_tokens = seq_metadata.num_kv_tokens

            if seq_metadata.is_kvp_request:
                if not started_kvp_seqs:
                    self.kvp_seqs_offset = qo_indptr[-1]
                    started_kvp_seqs = True

                self.kvp_seqs_qo_indptr.append(
                    self.kvp_seqs_qo_indptr[-1] + num_q_tokens
                )
                self.kvp_seqs_group_ids.append(seq_metadata.kvp_group_ids)
            else:
                assert not started_kvp_seqs, "Non-KVP sequences should come first."
                assert (
                    seq_metadata.save_kv_cache
                ), "Non-KVP sequences should save KV cache."

            num_q_tokens = seq_metadata.num_q_tokens
            num_kv_tokens = seq_metadata.num_kv_tokens

            if self.should_save_kv_cache:
                num_kv_tokens += num_q_tokens

            num_blocks_in_use = (num_kv_tokens + self.block_size - 1) // self.block_size
            num_blocks_in_use = min(num_blocks_in_use, len(seq_metadata.block_table))

            qo_indptr.append(qo_indptr[-1] + num_q_tokens)
            kv_page_indices.extend(seq_metadata.block_table[:num_blocks_in_use])
            kv_page_indptr.append(kv_page_indptr[-1] + num_blocks_in_use)
            kv_last_page_len.append(num_kv_tokens % self.block_size or self.block_size)

            if not self.should_save_kv_cache:
                continue

            for i in range(num_q_tokens):
                position_in_kv = i + seq_metadata.num_kv_tokens
                block_index = position_in_kv // self.block_size
                block_offset = position_in_kv % self.block_size
                block_num = seq_metadata.block_table[block_index]
                slot = block_num * self.block_size + block_offset
                slot_mapping.append(slot)

        self.num_q_tokens = qo_indptr[-1]

        qo_indptr_tensor = self._to_int_tensor(qo_indptr)
        kv_page_indptr_tensor = self._to_int_tensor(kv_page_indptr)
        kv_page_indices_tensor = self._to_int_tensor(kv_page_indices)
        kv_last_page_len_tensor = self._to_int_tensor(kv_last_page_len)

        assert self.wrapper is not None
        self.wrapper.plan(
            qo_indptr_tensor,
            kv_page_indptr_tensor,
            kv_page_indices_tensor,
            kv_last_page_len_tensor,
            self.num_q_heads,
            self.num_kv_heads,
            self.head_dim,
            self.block_size,
            non_blocking=True,
            causal=self.should_save_kv_cache,
        )

        if not self.should_save_kv_cache:
            return

        self.slot_mapping_tensor = self._to_long_tensor(slot_mapping)

    @check_metadata_initialized
    def end_forward(self):
        self.is_metadata_initialized = False
        if self.use_native_execution_backend:
            assert self.native_handle is not None
            self.native_handle.end_forward()

    @check_metadata_initialized
    def get_num_q_tokens(self) -> int:
        return self.num_q_tokens

    @check_metadata_initialized
    def save_kv_cache(
        self,
        key: torch.Tensor,
        value: torch.Tensor,
        kv_cache: torch.Tensor,
    ) -> None:
        if not self.should_save_kv_cache or self.is_no_op:
            return

        reshape_and_cache_flashinfer(
            key,
            value,
            kv_cache[:, 0],
            kv_cache[:, 1],
            self.slot_mapping_tensor,
        )

    @check_metadata_initialized
    def run(
        self,
        query: torch.Tensor,
        output: torch.Tensor,
        logsumexp: torch.Tensor,
        kv_cache: torch.Tensor,
    ) -> None:
        assert self.is_metadata_initialized

        if self.is_no_op:
            return

        if self.use_native_execution_backend:
            assert self.native_handle is not None
            self.native_handle.run(query, output, logsumexp, kv_cache)
            return

        assert self.wrapper is not None
        output[:], logsumexp[:] = self.wrapper.run(query, kv_cache, return_lse=True)

        if len(self.kvp_seqs_group_ids) > 0:
            # Perform online softmax reduction
            # TODO(Amey, Kasra): Integrate the new online softmax reduction kernel
            pass
