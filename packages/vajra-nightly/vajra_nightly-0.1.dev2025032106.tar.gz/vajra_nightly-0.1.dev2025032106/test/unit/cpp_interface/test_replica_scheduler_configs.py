import copy
import pickle
from typing import Any, cast

import pytest

from vajra.config import (
    BaseReplicaSchedulerConfig,
    EdfReplicaSchedulerConfig,
    FcfsFixedChunkReplicaSchedulerConfig,
    FcfsReplicaSchedulerConfig,
    LrsReplicaSchedulerConfig,
    StReplicaSchedulerConfig,
)
from vajra.enums import SchedulerType

EPSILON = 1e-5


# Base Replica Scheduler Config Tests
@pytest.mark.unit
def test_base_replica_scheduler_config_abstract():
    """Tests that BaseReplicaSchedulerConfig is an abstract class."""
    with pytest.raises(TypeError):
        BaseReplicaSchedulerConfig()  # type: ignore[abstract]


# FCFS Fixed Chunk Replica Scheduler Config Tests
@pytest.mark.parametrize(
    "max_batch_size, chunk_size",
    [(64, 1024), (128, 2048), (256, 4096)],
)
@pytest.mark.unit
def test_valid_fcfs_fixed_chunk_config_creation(max_batch_size, chunk_size):
    """Tests creating valid FcfsFixedChunkReplicaSchedulerConfig objects and accessing their properties."""
    config = FcfsFixedChunkReplicaSchedulerConfig(
        max_batch_size=max_batch_size, chunk_size=chunk_size
    )
    config_c = cast(Any, config.native_handle)
    assert config.max_batch_size == config_c.max_batch_size
    assert config.chunk_size == config_c.chunk_size
    assert config.get_max_num_batched_tokens() == chunk_size
    assert config.get_type() == SchedulerType.FCFS_FIXED_CHUNK


@pytest.mark.parametrize(
    "max_batch_size, chunk_size",
    [(64, 1024), (128, 2048), (256, 4096)],
)
@pytest.mark.unit
def test_can_deep_copy_fcfs_fixed_chunk_config(max_batch_size, chunk_size):
    """Tests deep copying valid FcfsFixedChunkReplicaSchedulerConfig objects and accessing their properties."""
    config = FcfsFixedChunkReplicaSchedulerConfig(
        max_batch_size=max_batch_size, chunk_size=chunk_size
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.max_batch_size == config_deep_copy.max_batch_size
    assert config.chunk_size == config_deep_copy.chunk_size
    assert (
        config.get_max_num_batched_tokens()
        == config_deep_copy.get_max_num_batched_tokens()
    )


@pytest.mark.parametrize(
    "max_batch_size, chunk_size",
    [(64, 1024), (128, 2048), (256, 4096)],
)
@pytest.mark.unit
def test_can_pickle_fcfs_fixed_chunk_config(max_batch_size, chunk_size):
    """Tests pickling FcfsFixedChunkReplicaSchedulerConfig objects and accessing their properties."""
    config = FcfsFixedChunkReplicaSchedulerConfig(
        max_batch_size=max_batch_size, chunk_size=chunk_size
    )
    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)
    assert config.max_batch_size == config_from_pickle.max_batch_size
    assert config.chunk_size == config_from_pickle.chunk_size
    assert (
        config.get_max_num_batched_tokens()
        == config_from_pickle.get_max_num_batched_tokens()
    )


# FCFS Replica Scheduler Config Tests
@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time",
    [
        (64, 4096, 16, 0.04),
        (128, 8192, 32, 0.05),
        (256, 16384, 64, 0.06),
    ],
)
@pytest.mark.unit
def test_valid_fcfs_config_creation(
    max_batch_size, max_chunk_size, min_chunk_size, target_batch_time
):
    """Tests creating valid FcfsReplicaSchedulerConfig objects and accessing their properties."""
    config = FcfsReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
    )
    config_c = cast(Any, config.native_handle)
    assert config.max_batch_size == config_c.max_batch_size
    assert config.max_chunk_size == config_c.max_chunk_size
    assert config.min_chunk_size == config_c.min_chunk_size
    assert abs(config.target_batch_time - config_c.target_batch_time) < EPSILON
    assert config.get_max_num_batched_tokens() == max_chunk_size
    assert config.get_type() == SchedulerType.FCFS


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time",
    [
        (64, 4096, 16, 0.04),
        (128, 8192, 32, 0.05),
        (256, 16384, 64, 0.06),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_fcfs_config(
    max_batch_size, max_chunk_size, min_chunk_size, target_batch_time
):
    """Tests deep copying valid FcfsReplicaSchedulerConfig objects and accessing their properties."""
    config = FcfsReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.max_batch_size == config_deep_copy.max_batch_size
    assert config.max_chunk_size == config_deep_copy.max_chunk_size
    assert config.min_chunk_size == config_deep_copy.min_chunk_size
    assert abs(config.target_batch_time - config_deep_copy.target_batch_time) < EPSILON
    assert (
        config.get_max_num_batched_tokens()
        == config_deep_copy.get_max_num_batched_tokens()
    )


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time",
    [
        (64, 4096, 16, 0.04),
        (128, 8192, 32, 0.05),
        (256, 16384, 64, 0.06),
    ],
)
@pytest.mark.unit
def test_can_pickle_fcfs_config(
    max_batch_size, max_chunk_size, min_chunk_size, target_batch_time
):
    """Tests pickling FcfsReplicaSchedulerConfig objects and accessing their properties."""
    config = FcfsReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
    )
    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)
    assert config.max_batch_size == config_from_pickle.max_batch_size
    assert config.max_chunk_size == config_from_pickle.max_chunk_size
    assert config.min_chunk_size == config_from_pickle.min_chunk_size
    assert (
        abs(config.target_batch_time - config_from_pickle.target_batch_time) < EPSILON
    )
    assert (
        config.get_max_num_batched_tokens()
        == config_from_pickle.get_max_num_batched_tokens()
    )


# EDF Replica Scheduler Config Tests
@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3),
        (128, 8192, 32, 0.05, 1.5, 0.5),
        (256, 16384, 64, 0.06, 1.8, 0.7),
    ],
)
@pytest.mark.unit
def test_valid_edf_config_creation(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
):
    """Tests creating valid EdfReplicaSchedulerConfig objects and accessing their properties."""
    config = EdfReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
    )
    config_c = cast(Any, config.native_handle)
    assert config.max_batch_size == config_c.max_batch_size
    assert config.max_chunk_size == config_c.max_chunk_size
    assert config.min_chunk_size == config_c.min_chunk_size
    assert abs(config.target_batch_time - config_c.target_batch_time) < EPSILON
    assert abs(config.deadline_multiplier - config_c.deadline_multiplier) < EPSILON
    assert abs(config.min_deadline - config_c.min_deadline) < EPSILON
    assert config.get_max_num_batched_tokens() == max_chunk_size
    assert config.get_type() == SchedulerType.EDF


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3),
        (128, 8192, 32, 0.05, 1.5, 0.5),
        (256, 16384, 64, 0.06, 1.8, 0.7),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_edf_config(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
):
    """Tests deep copying valid EdfReplicaSchedulerConfig objects and accessing their properties."""
    config = EdfReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.max_batch_size == config_deep_copy.max_batch_size
    assert config.max_chunk_size == config_deep_copy.max_chunk_size
    assert config.min_chunk_size == config_deep_copy.min_chunk_size
    assert abs(config.target_batch_time - config_deep_copy.target_batch_time) < EPSILON
    assert (
        abs(config.deadline_multiplier - config_deep_copy.deadline_multiplier) < EPSILON
    )
    assert abs(config.min_deadline - config_deep_copy.min_deadline) < EPSILON
    assert (
        config.get_max_num_batched_tokens()
        == config_deep_copy.get_max_num_batched_tokens()
    )


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3),
        (128, 8192, 32, 0.05, 1.5, 0.5),
        (256, 16384, 64, 0.06, 1.8, 0.7),
    ],
)
@pytest.mark.unit
def test_can_pickle_edf_config(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
):
    """Tests pickling EdfReplicaSchedulerConfig objects and accessing their properties."""
    config = EdfReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
    )
    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)
    assert config.max_batch_size == config_from_pickle.max_batch_size
    assert config.max_chunk_size == config_from_pickle.max_chunk_size
    assert config.min_chunk_size == config_from_pickle.min_chunk_size
    assert (
        abs(config.target_batch_time - config_from_pickle.target_batch_time) < EPSILON
    )
    assert (
        abs(config.deadline_multiplier - config_from_pickle.deadline_multiplier)
        < EPSILON
    )
    assert abs(config.min_deadline - config_from_pickle.min_deadline) < EPSILON
    assert (
        config.get_max_num_batched_tokens()
        == config_from_pickle.get_max_num_batched_tokens()
    )


# LRS Replica Scheduler Config Tests
@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3),
        (128, 8192, 32, 0.05, 1.5, 0.5),
        (256, 16384, 64, 0.06, 1.8, 0.7),
    ],
)
@pytest.mark.unit
def test_valid_lrs_config_creation(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
):
    """Tests creating valid LrsReplicaSchedulerConfig objects and accessing their properties."""
    config = LrsReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
    )
    config_c = cast(Any, config.native_handle)
    assert config.max_batch_size == config_c.max_batch_size
    assert config.max_chunk_size == config_c.max_chunk_size
    assert config.min_chunk_size == config_c.min_chunk_size
    assert abs(config.target_batch_time - config_c.target_batch_time) < EPSILON
    assert abs(config.deadline_multiplier - config_c.deadline_multiplier) < EPSILON
    assert abs(config.min_deadline - config_c.min_deadline) < EPSILON
    assert config.get_max_num_batched_tokens() == max_chunk_size
    assert config.get_type() == SchedulerType.LRS


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3),
        (128, 8192, 32, 0.05, 1.5, 0.5),
        (256, 16384, 64, 0.06, 1.8, 0.7),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_lrs_config(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
):
    """Tests deep copying valid LrsReplicaSchedulerConfig objects and accessing their properties."""
    config = LrsReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.max_batch_size == config_deep_copy.max_batch_size
    assert config.max_chunk_size == config_deep_copy.max_chunk_size
    assert config.min_chunk_size == config_deep_copy.min_chunk_size
    assert abs(config.target_batch_time - config_deep_copy.target_batch_time) < EPSILON
    assert (
        abs(config.deadline_multiplier - config_deep_copy.deadline_multiplier) < EPSILON
    )
    assert abs(config.min_deadline - config_deep_copy.min_deadline) < EPSILON
    assert (
        config.get_max_num_batched_tokens()
        == config_deep_copy.get_max_num_batched_tokens()
    )


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3),
        (128, 8192, 32, 0.05, 1.5, 0.5),
        (256, 16384, 64, 0.06, 1.8, 0.7),
    ],
)
@pytest.mark.unit
def test_can_pickle_lrs_config(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
):
    """Tests pickling LrsReplicaSchedulerConfig objects and accessing their properties."""
    config = LrsReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
    )
    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)
    assert config.max_batch_size == config_from_pickle.max_batch_size
    assert config.max_chunk_size == config_from_pickle.max_chunk_size
    assert config.min_chunk_size == config_from_pickle.min_chunk_size
    assert (
        abs(config.target_batch_time - config_from_pickle.target_batch_time) < EPSILON
    )
    assert (
        abs(config.deadline_multiplier - config_from_pickle.deadline_multiplier)
        < EPSILON
    )
    assert abs(config.min_deadline - config_from_pickle.min_deadline) < EPSILON
    assert (
        config.get_max_num_batched_tokens()
        == config_from_pickle.get_max_num_batched_tokens()
    )


# ST Replica Scheduler Config Tests
@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline, long_seq_threshold",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3, 128 * 1024),
        (128, 8192, 32, 0.05, 1.5, 0.5, 256 * 1024),
        (256, 16384, 64, 0.06, 1.8, 0.7, 512 * 1024),
    ],
)
@pytest.mark.unit
def test_valid_st_config_creation(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
    long_seq_threshold,
):
    """Tests creating valid StReplicaSchedulerConfig objects and accessing their properties."""
    config = StReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
        long_seq_kv_cache_len_threshold=long_seq_threshold,
    )
    config_c = cast(Any, config.native_handle)
    assert config.max_batch_size == config_c.max_batch_size
    assert config.max_chunk_size == config_c.max_chunk_size
    assert config.min_chunk_size == config_c.min_chunk_size
    assert abs(config.target_batch_time - config_c.target_batch_time) < EPSILON
    assert abs(config.deadline_multiplier - config_c.deadline_multiplier) < EPSILON
    assert abs(config.min_deadline - config_c.min_deadline) < EPSILON
    assert (
        config.long_seq_kv_cache_len_threshold
        == config_c.long_seq_kv_cache_len_threshold
    )
    assert config.get_max_num_batched_tokens() == max_chunk_size
    assert config.get_type() == SchedulerType.ST


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline, long_seq_threshold",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3, 128 * 1024),
        (128, 8192, 32, 0.05, 1.5, 0.5, 256 * 1024),
        (256, 16384, 64, 0.06, 1.8, 0.7, 512 * 1024),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_st_config(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
    long_seq_threshold,
):
    """Tests deep copying valid StReplicaSchedulerConfig objects and accessing their properties."""
    config = StReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
        long_seq_kv_cache_len_threshold=long_seq_threshold,
    )
    config_deep_copy = copy.deepcopy(config)
    assert config.max_batch_size == config_deep_copy.max_batch_size
    assert config.max_chunk_size == config_deep_copy.max_chunk_size
    assert config.min_chunk_size == config_deep_copy.min_chunk_size
    assert abs(config.target_batch_time - config_deep_copy.target_batch_time) < EPSILON
    assert (
        abs(config.deadline_multiplier - config_deep_copy.deadline_multiplier) < EPSILON
    )
    assert abs(config.min_deadline - config_deep_copy.min_deadline) < EPSILON
    assert (
        config.long_seq_kv_cache_len_threshold
        == config_deep_copy.long_seq_kv_cache_len_threshold
    )
    assert (
        config.get_max_num_batched_tokens()
        == config_deep_copy.get_max_num_batched_tokens()
    )


@pytest.mark.parametrize(
    "max_batch_size, max_chunk_size, min_chunk_size, target_batch_time, deadline_multiplier, min_deadline, long_seq_threshold",
    [
        (64, 4096, 16, 0.04, 1.2, 0.3, 128 * 1024),
        (128, 8192, 32, 0.05, 1.5, 0.5, 256 * 1024),
        (256, 16384, 64, 0.06, 1.8, 0.7, 512 * 1024),
    ],
)
@pytest.mark.unit
def test_can_pickle_st_config(
    max_batch_size,
    max_chunk_size,
    min_chunk_size,
    target_batch_time,
    deadline_multiplier,
    min_deadline,
    long_seq_threshold,
):
    """Tests pickling StReplicaSchedulerConfig objects and accessing their properties."""
    config = StReplicaSchedulerConfig(
        max_batch_size=max_batch_size,
        max_chunk_size=max_chunk_size,
        min_chunk_size=min_chunk_size,
        target_batch_time=target_batch_time,
        deadline_multiplier=deadline_multiplier,
        min_deadline=min_deadline,
        long_seq_kv_cache_len_threshold=long_seq_threshold,
    )
    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)
    assert config.max_batch_size == config_from_pickle.max_batch_size
    assert config.max_chunk_size == config_from_pickle.max_chunk_size
    assert config.min_chunk_size == config_from_pickle.min_chunk_size
    assert (
        abs(config.target_batch_time - config_from_pickle.target_batch_time) < EPSILON
    )
    assert (
        abs(config.deadline_multiplier - config_from_pickle.deadline_multiplier)
        < EPSILON
    )
    assert abs(config.min_deadline - config_from_pickle.min_deadline) < EPSILON
    assert (
        config.long_seq_kv_cache_len_threshold
        == config_from_pickle.long_seq_kv_cache_len_threshold
    )
    assert (
        config.get_max_num_batched_tokens()
        == config_from_pickle.get_max_num_batched_tokens()
    )
