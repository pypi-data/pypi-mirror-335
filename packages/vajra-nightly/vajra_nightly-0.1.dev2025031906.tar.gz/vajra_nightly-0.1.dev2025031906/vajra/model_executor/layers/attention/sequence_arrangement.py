from abc import ABC, abstractmethod
from typing import List, Union

from vajra.datatypes import SequenceMetadata  # type: ignore

LONG_REQUEST_THRESHOLD = 256 * 1024  # 256K

ContainerType = Union[List, "_BaseSequenceArrangement"]


class _BaseSequenceArrangement(ABC):
    def __init__(self):
        self.r1: ContainerType = self.get_container()
        self.r2: ContainerType = self.get_container()

    def append(self, seq_metadata: SequenceMetadata) -> None:
        if self.check_predicate(seq_metadata):
            self.r1.append(seq_metadata)
        else:
            self.r2.append(seq_metadata)

    def extend(self, seq_metadata_list: List[SequenceMetadata]) -> None:
        for seq_metadata in seq_metadata_list:
            self.append(seq_metadata)

    def check_arrangement_and_extend(
        self, seq_metadata_list: List[SequenceMetadata]
    ) -> None:
        started_r2 = False
        r1_seq_metadata = []
        r2_seq_metadata = []

        for seq_metadata in seq_metadata_list:
            if self.check_predicate(seq_metadata):
                assert not started_r2, "Sequence metadata list is not sorted"
                r1_seq_metadata.append(seq_metadata)
            else:
                started_r2 = True
                r2_seq_metadata.append(seq_metadata)

        if isinstance(self.r1, _BaseSequenceArrangement) and isinstance(
            self.r2, _BaseSequenceArrangement
        ):
            self.r1.check_arrangement_and_extend(r1_seq_metadata)
            self.r2.check_arrangement_and_extend(r2_seq_metadata)
        else:
            self.r1.extend(r1_seq_metadata)
            self.r2.extend(r2_seq_metadata)

    def get_arranged(self) -> List[SequenceMetadata]:
        if isinstance(self.r1, _BaseSequenceArrangement) and isinstance(
            self.r2, _BaseSequenceArrangement
        ):
            return self.r1.get_arranged() + self.r2.get_arranged()

        assert isinstance(self.r1, list) and isinstance(self.r2, list)

        return self.r1 + self.r2

    def get_splits(self) -> List[List[SequenceMetadata]]:
        if isinstance(self.r1, _BaseSequenceArrangement) and isinstance(
            self.r2, _BaseSequenceArrangement
        ):
            return [*self.r1.get_splits(), *self.r2.get_splits()]

        assert isinstance(self.r1, list) and isinstance(self.r2, list)

        return [self.r1 + self.r2]

    @classmethod
    def get_num_splits(cls) -> int:
        container = cls.get_container()
        if isinstance(container, _BaseSequenceArrangement):
            return 2 * container.get_num_splits()

        return 1

    @classmethod
    def get_container(cls) -> ContainerType:
        raise NotImplemented

    @abstractmethod
    def check_predicate(self, seq_metadata: SequenceMetadata) -> bool:
        raise NotImplemented


class _SequenceGroupArrangement(_BaseSequenceArrangement):
    @classmethod
    def get_container(cls) -> ContainerType:
        return []

    def check_predicate(self, seq_metadata: SequenceMetadata) -> bool:
        return not seq_metadata.is_kvp_request


class _SaveKvCacheBasedSequenceArrangement(_BaseSequenceArrangement):
    @classmethod
    def get_container(cls) -> ContainerType:
        return _SequenceGroupArrangement()

    def check_predicate(self, seq_metadata: SequenceMetadata) -> bool:
        return seq_metadata.save_kv_cache


class _LengthBasedSequenceArrangement(_BaseSequenceArrangement):
    @classmethod
    def get_container(cls) -> ContainerType:
        return _SaveKvCacheBasedSequenceArrangement()

    def check_predicate(self, seq_metadata: SequenceMetadata) -> bool:
        return seq_metadata.num_kv_tokens > LONG_REQUEST_THRESHOLD


class SequenceArrangement(_BaseSequenceArrangement):
    """
    We need to arrange sequences in a way that allows us to perform
    attention computation in an efficient manner. Due to poor handling of mixed batches
    in attention kernels. We need to split the first split the sequences into prefill and decode:
    | prefill seqs | decode seqs |

    Secondly, when we mix sequences of different lengths, the attention kernel parallelization
    heuristics fail, and results in high latency. Thus, we need to further split the sequences:
    | long seqs | short seqs |

    Furthermore, within each group, we can have kvp sequences. Some of these kvp
    sequences might not require kv cache to be saved. So, within each group, we need to further
    organize sequences as follows:
    | seqs w/ save_kv_cache | seqs w/o save_kv_cache |

    Finally, we need to organize the sequences in a way that allows us to perform kvp reduction
    in an efficient manner. We need to organize the sequences in the following way:
    | non kvp seqs | kvp seqs |
    However, for this last bit, we don't need to make a separate kernel call, just sorting the sequences
    in this order is sufficient.
    """

    @classmethod
    def get_container(cls) -> ContainerType:
        return _LengthBasedSequenceArrangement()

    def check_predicate(self, seq_metadata: SequenceMetadata) -> bool:
        return seq_metadata.num_q_tokens > 1
