from typing import List

import pytest

from vajra._native.model_executor import SequenceArrangement as SequenceArrangementC
from vajra.datatypes import SequenceMetadata  # type: ignore
from vajra.model_executor.layers.attention.sequence_arrangement import (
    SequenceArrangement,
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
class TestSequenceArrangement:
    def test_empty_sequence_list(self):
        """Test behavior with an empty sequence list."""
        sequence_arrangement = SequenceArrangement()
        sequence_arrangement_native = SequenceArrangementC()

        # Process empty sequence list
        sequence_arrangement.check_arrangement_and_extend([])
        sequence_arrangement_native.check_arrangement_and_extend([])

        # Check splits
        splits = sequence_arrangement.get_splits()
        splits_native = sequence_arrangement_native.get_splits()

        assert len(splits) == len(splits_native)
        assert splits == splits_native

    def test_single_sequence(self):
        """Test behavior with a single sequence."""
        sequence_arrangement = SequenceArrangement()
        sequence_arrangement_native = SequenceArrangementC()

        # Create a single sequence
        seq_metadata = create_sequence_metadata("test_seq", 4, 8, [0, 1, 2, 3], True)

        # Process the sequence
        sequence_arrangement.check_arrangement_and_extend([seq_metadata])
        sequence_arrangement_native.check_arrangement_and_extend([seq_metadata])

        # Check splits
        splits = sequence_arrangement.get_splits()
        splits_native = sequence_arrangement_native.get_splits()

        assert len(splits) == len(splits_native)
        for split, split_native in zip(splits, splits_native):
            assert len(split) == len(split_native)
            for seq, seq_native in zip(split, split_native):
                assert seq.seq_id == seq_native.seq_id
                assert seq.num_q_tokens == seq_native.num_q_tokens
                assert seq.num_kv_tokens == seq_native.num_kv_tokens
                assert seq.block_table == seq_native.block_table

    def test_multiple_sequences(self):
        """Test behavior with multiple sequences."""
        sequence_arrangement = SequenceArrangement()
        sequence_arrangement_native = SequenceArrangementC()

        # Create multiple sequences
        seq_metadata1 = create_sequence_metadata(
            "test_seq1", 4, 8, [1, 2, 3, 4], True, [0]
        )
        seq_metadata2 = create_sequence_metadata(
            "test_seq2", 2, 12, [4, 5, 6, 7], True, [0, 1]
        )
        seq_metadata3 = create_sequence_metadata(
            "test_seq3", 8, 4, [8, 9, 10, 11], False, [0]
        )
        seq_metadata4 = create_sequence_metadata(
            "test_seq4", 6, 8, [12, 13, 14, 15], False, [0, 1]
        )
        seq_metadata5 = create_sequence_metadata(
            "test_seq5", 1, 8, [16, 17, 18, 19], True, [0]
        )
        seq_metadata6 = create_sequence_metadata(
            "test_seq6", 1, 12, [20, 21, 22, 23], True, [0, 1]
        )
        seq_metadata7 = create_sequence_metadata(
            "test_seq7", 1, 4, [24, 25, 26, 27], False, [0]
        )
        seq_metadata8 = create_sequence_metadata(
            "test_seq8", 1, 8, [28, 29, 30, 31], False, [0, 1]
        )

        # Process the sequences
        sequence_arrangement.check_arrangement_and_extend(
            [
                seq_metadata1,
                seq_metadata2,
                seq_metadata3,
                seq_metadata4,
                seq_metadata5,
                seq_metadata6,
                seq_metadata7,
                seq_metadata8,
            ]
        )
        sequence_arrangement_native.check_arrangement_and_extend(
            [
                seq_metadata1,
                seq_metadata2,
                seq_metadata3,
                seq_metadata4,
                seq_metadata5,
                seq_metadata6,
                seq_metadata7,
                seq_metadata8,
            ]
        )

        # Check splits
        splits = sequence_arrangement.get_splits()
        splits_native = sequence_arrangement_native.get_splits()

        assert len(splits) == len(splits_native)
        for split, split_native in zip(splits, splits_native):
            assert len(split) == len(split_native)
            for seq, seq_native in zip(split, split_native):
                assert seq.seq_id == seq_native.seq_id
                assert seq.num_q_tokens == seq_native.num_q_tokens
                assert seq.num_kv_tokens == seq_native.num_kv_tokens
                assert seq.block_table == seq_native.block_table
                assert seq.kvp_group_ids == seq_native.kvp_group_ids

        # Check arranged output
        arranged = sequence_arrangement.get_arranged()
        arranged_native = sequence_arrangement_native.get_arranged()

        assert len(arranged) == len(arranged_native)
        for seq, seq_native in zip(arranged, arranged_native):
            assert seq.seq_id == seq_native.seq_id
            assert seq.num_q_tokens == seq_native.num_q_tokens
            assert seq.num_kv_tokens == seq_native.num_kv_tokens
            assert seq.block_table == seq_native.block_table
            assert seq.kvp_group_ids == seq_native.kvp_group_ids

    def test_num_splits(self):
        """Test the number of splits."""
        sequence_arrangement = SequenceArrangement()
        sequence_arrangement_native = SequenceArrangementC()

        # Create sequences
        seq_metadata1 = create_sequence_metadata(
            "test_seq1", 4, 8, [0, 1, 2, 3], True, [0]
        )
        seq_metadata2 = create_sequence_metadata(
            "test_seq2", 2, 12, [4, 5, 6, 7], True, [0, 1]
        )

        # Process the sequences
        sequence_arrangement.check_arrangement_and_extend(
            [seq_metadata1, seq_metadata2]
        )
        sequence_arrangement_native.check_arrangement_and_extend(
            [seq_metadata1, seq_metadata2]
        )

        # Check number of splits
        assert (
            sequence_arrangement.get_num_splits()
            == sequence_arrangement_native.get_num_splits()
        )
        assert (
            len(sequence_arrangement.get_splits())
            == sequence_arrangement.get_num_splits()
        )
        assert (
            len(sequence_arrangement_native.get_splits())
            == sequence_arrangement_native.get_num_splits()
        )
