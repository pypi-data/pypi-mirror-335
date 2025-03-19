from typing import Any, Dict, List

import pytest
import torch

from vajra.datatypes import SequenceMetadata  # type: ignore
from vajra.model_executor.layers.attention.flashinfer_attention_wrapper import (
    FlashinferAttentionWrapper,
)


def create_sequence_metadata(
    seq_id: str,
    num_q_tokens: int,
    num_kv_tokens: int,
    block_table: List[int],
    save_kv_cache: bool = True,
    kvp_group_ids: List[int] = [0],
) -> SequenceMetadata:
    """Helper function to create a sequence metadata object for testing."""
    metadata = SequenceMetadata(
        0,
        seq_id,
        num_q_tokens,
        num_kv_tokens,
        block_table,
        kvp_group_ids,
        save_kv_cache,
    )

    return metadata


@pytest.mark.unit
class TestFlashinferAttentionWrapper:
    @pytest.fixture
    def setup_wrapper(self) -> Dict[str, Any]:
        """Setup the wrapper for testing."""
        # Parameters
        num_q_heads = 8
        num_kv_heads = 8
        head_dim = 64
        block_size = 4
        device = torch.device("cuda")

        # Create both native and non-native wrappers for testing
        native_wrapper = FlashinferAttentionWrapper(
            num_q_heads=num_q_heads,
            num_kv_heads=num_kv_heads,
            head_dim=head_dim,
            block_size=block_size,
            use_native_execution_backend=True,
            device=device,
        )

        python_wrapper = FlashinferAttentionWrapper(
            num_q_heads=num_q_heads,
            num_kv_heads=num_kv_heads,
            head_dim=head_dim,
            block_size=block_size,
            use_native_execution_backend=False,
            device=device,
        )

        return {
            "native_wrapper": native_wrapper,
            "python_wrapper": python_wrapper,
            "num_q_heads": num_q_heads,
            "num_kv_heads": num_kv_heads,
            "head_dim": head_dim,
            "block_size": block_size,
            "device": device,
        }

    def test_initialization(self, setup_wrapper: Dict[str, Any]):
        """Test that the wrapper initializes correctly."""
        native_wrapper = setup_wrapper["native_wrapper"]
        python_wrapper = setup_wrapper["python_wrapper"]

        # Check initial state for both wrappers
        assert native_wrapper.is_metadata_initialized is False
        assert python_wrapper.is_metadata_initialized is False

        assert native_wrapper.is_no_op is False
        assert python_wrapper.is_no_op is False

        assert native_wrapper.should_save_kv_cache is False
        assert python_wrapper.should_save_kv_cache is False

        assert native_wrapper.num_q_tokens == 0
        assert python_wrapper.num_q_tokens == 0

        # Check that native_wrapper has the C++ wrapper initialized
        assert native_wrapper.native_handle is not None
        assert python_wrapper.native_handle is None

    def test_empty_sequence_list(self, setup_wrapper: Dict[str, Any]):
        """Test behavior with an empty sequence list."""
        native_wrapper = setup_wrapper["native_wrapper"]
        python_wrapper = setup_wrapper["python_wrapper"]

        # Process empty sequence list
        native_wrapper.begin_forward([])
        python_wrapper.begin_forward([])

        # Check state after processing
        assert native_wrapper.is_metadata_initialized is True
        assert python_wrapper.is_metadata_initialized is True

        assert native_wrapper.is_no_op is True
        assert python_wrapper.is_no_op is True

        assert native_wrapper.num_q_tokens == 0
        assert python_wrapper.num_q_tokens == 0

    def test_single_sequence(self, setup_wrapper: Dict[str, Any]):
        """Test behavior with a single sequence."""
        native_wrapper = setup_wrapper["native_wrapper"]
        python_wrapper = setup_wrapper["python_wrapper"]
        block_size = setup_wrapper["block_size"]

        # Create a single sequence
        seq_metadata = create_sequence_metadata("test_seq", 4, 8, [0, 1, 2, 3], True)

        # Process the sequence
        native_wrapper.begin_forward([seq_metadata])
        python_wrapper.begin_forward([seq_metadata])

        # Check state after processing
        assert native_wrapper.is_no_op is False
        assert python_wrapper.is_no_op is False

        assert native_wrapper.num_q_tokens == 4
        assert python_wrapper.num_q_tokens == 4

        assert native_wrapper.should_save_kv_cache is True
        assert python_wrapper.should_save_kv_cache is True

        # Check that slot_mapping_tensor is created
        assert native_wrapper.slot_mapping_tensor is not None
        assert python_wrapper.slot_mapping_tensor is not None

        assert native_wrapper.slot_mapping_tensor.size(0) == 4
        assert python_wrapper.slot_mapping_tensor.size(0) == 4

        # Check that slot_mapping_tensor is equal
        assert torch.equal(
            native_wrapper.slot_mapping_tensor, python_wrapper.slot_mapping_tensor
        )

    def test_multiple_sequences(self, setup_wrapper: Dict[str, Any]):
        """Test behavior with multiple sequences."""
        native_wrapper = setup_wrapper["native_wrapper"]
        python_wrapper = setup_wrapper["python_wrapper"]
        block_size = setup_wrapper["block_size"]

        # Create multiple sequences
        seq_metadata1 = create_sequence_metadata("test_seq1", 4, 8, [0, 1, 2, 3], True)
        seq_metadata2 = create_sequence_metadata("test_seq2", 2, 12, [4, 5, 6, 7], True)

        # Process the sequences
        native_wrapper.begin_forward([seq_metadata1, seq_metadata2])
        python_wrapper.begin_forward([seq_metadata1, seq_metadata2])

        # Check state after processing
        assert native_wrapper.num_q_tokens == 6
        assert python_wrapper.num_q_tokens == 6

        assert native_wrapper.should_save_kv_cache is True
        assert python_wrapper.should_save_kv_cache is True

        # Check that slot_mapping_tensor is created with correct size
        assert native_wrapper.slot_mapping_tensor.size(0) == 6
        assert python_wrapper.slot_mapping_tensor.size(0) == 6

        # Check that slot_mapping_tensor is equal
        assert torch.equal(
            native_wrapper.slot_mapping_tensor, python_wrapper.slot_mapping_tensor
        )

    def test_no_save_kv_cache(self, setup_wrapper: Dict[str, Any]):
        """Test behavior when not saving KV cache."""
        native_wrapper = setup_wrapper["native_wrapper"]
        python_wrapper = setup_wrapper["python_wrapper"]
        block_size = setup_wrapper["block_size"]

        # Create sequences that don't save KV cache
        seq_metadata1 = create_sequence_metadata(
            "test_seq1", 4, 8, [0, 1, 2, 3], False, [0, 1]
        )
        seq_metadata2 = create_sequence_metadata(
            "test_seq2", 2, 12, [4, 5, 6, 7], False, [0, 1]
        )

        # Process the sequences
        native_wrapper.begin_forward([seq_metadata1, seq_metadata2])
        python_wrapper.begin_forward([seq_metadata1, seq_metadata2])

        # Check state after processing
        assert native_wrapper.num_q_tokens == 6
        assert python_wrapper.num_q_tokens == 6

        assert native_wrapper.should_save_kv_cache is False
        assert python_wrapper.should_save_kv_cache is False

        # slot_mapping_tensor should not be created when not saving KV cache
        assert (
            not hasattr(native_wrapper, "slot_mapping_tensor")
            or native_wrapper.slot_mapping_tensor is None
        )
        assert (
            not hasattr(python_wrapper, "slot_mapping_tensor")
            or python_wrapper.slot_mapping_tensor is None
        )

    def test_end_forward(self, setup_wrapper: Dict[str, Any]):
        """Test the end_forward method."""
        native_wrapper = setup_wrapper["native_wrapper"]
        python_wrapper = setup_wrapper["python_wrapper"]
        block_size = setup_wrapper["block_size"]

        # Create and process a sequence
        seq_metadata = create_sequence_metadata("test_seq", 4, 8, [0, 1, 2, 3], True)
        native_wrapper.begin_forward([seq_metadata])
        python_wrapper.begin_forward([seq_metadata])

        # End forward
        native_wrapper.end_forward()
        python_wrapper.end_forward()

        # Check that metadata is no longer initialized
        assert native_wrapper.is_metadata_initialized is False
        assert python_wrapper.is_metadata_initialized is False
