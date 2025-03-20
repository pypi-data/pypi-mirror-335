import copy
import pickle

import pytest

from vajra.config import (
    BaseReplicaControllerConfig,
    CacheConfig,
    LlmReplicaControllerConfig,
    LlmReplicasetControllerConfig,
    MetricsConfig,
    ModelConfig,
    ParallelConfig,
    PullReplicasetSchedulerConfig,
    StReplicaSchedulerConfig,
    WorkerConfig,
)
from vajra.enums import (
    ReplicaControllerType,
)


def compare_attributes(obj1, obj2):
    for attr, value in vars(obj1).items():
        if attr != "native_handle" and getattr(obj2, attr, None) != value:
            print(
                f"Mismatch found: {attr} -> obj1: {value}, obj2: {getattr(obj2, attr)}"
            )
            return False
    return True


@pytest.mark.parametrize(
    "model_config, worker_config, cache_config, parallel_config, scheduler_config, metrics_config",
    [
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(block_size=32, num_gpu_blocks=1024),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
    ],
)
@pytest.mark.unit
def test_base_replica_controller_config_creation(
    model_config,
    worker_config,
    cache_config,
    parallel_config,
    scheduler_config,
    metrics_config,
):
    """Tests creating valid BaseReplicaControllerConfig objects and accessing their properties."""
    config = BaseReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        scheduler_config=scheduler_config,
        metrics_config=metrics_config,
    )

    assert config.model_config == model_config
    assert config.worker_config == worker_config
    assert config.cache_config == cache_config
    assert config.parallel_config == parallel_config
    assert config.scheduler_config == scheduler_config
    assert config.metrics_config == metrics_config

    assert config.native_handle is not None  # pyright: ignore


@pytest.mark.parametrize(
    "model_config, worker_config, cache_config, parallel_config, scheduler_config, metrics_config",
    [
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(block_size=32, num_gpu_blocks=1024),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_base_replica_controller_config(
    model_config,
    worker_config,
    cache_config,
    parallel_config,
    scheduler_config,
    metrics_config,
):
    """Tests deep copying valid BaseReplicaControllerConfig objects and accessing their properties."""
    config = BaseReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        scheduler_config=scheduler_config,
        metrics_config=metrics_config,
    )

    config_deep_copy = copy.deepcopy(config)

    assert config.model_config == config_deep_copy.model_config
    assert config.worker_config == config_deep_copy.worker_config
    assert config.cache_config == config_deep_copy.cache_config
    assert config.parallel_config == config_deep_copy.parallel_config
    assert (
        compare_attributes(config.scheduler_config, config_deep_copy.scheduler_config)
        == True
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_batch_size
        == config_deep_copy.scheduler_config.native_handle.max_batch_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_chunk_size
        == config_deep_copy.scheduler_config.native_handle.max_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_chunk_size
        == config_deep_copy.scheduler_config.native_handle.min_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.target_batch_time
        == config_deep_copy.scheduler_config.native_handle.target_batch_time
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.deadline_multiplier
        == config_deep_copy.scheduler_config.native_handle.deadline_multiplier
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_deadline
        == config_deep_copy.scheduler_config.native_handle.min_deadline
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
        == config_deep_copy.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
    )
    assert config.metrics_config == config_deep_copy.metrics_config

    assert config is not config_deep_copy


@pytest.mark.parametrize(
    "model_config, worker_config, cache_config, parallel_config, scheduler_config, metrics_config",
    [
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(block_size=32, num_gpu_blocks=1024),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
    ],
)
@pytest.mark.unit
def test_can_pickle_base_replica_controller_config(
    model_config,
    worker_config,
    cache_config,
    parallel_config,
    scheduler_config,
    metrics_config,
):
    """Tests pickling BaseReplicaControllerConfig objects and accessing their properties."""
    config = BaseReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        scheduler_config=scheduler_config,
        metrics_config=metrics_config,
    )

    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)

    assert config.model_config == config_from_pickle.model_config
    assert config.worker_config == config_from_pickle.worker_config
    assert config.cache_config == config_from_pickle.cache_config
    assert config.parallel_config == config_from_pickle.parallel_config
    assert (
        compare_attributes(config.scheduler_config, config_from_pickle.scheduler_config)
        == True
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_batch_size
        == config_from_pickle.scheduler_config.native_handle.max_batch_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_chunk_size
        == config_from_pickle.scheduler_config.native_handle.max_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_chunk_size
        == config_from_pickle.scheduler_config.native_handle.min_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.target_batch_time
        == config_from_pickle.scheduler_config.native_handle.target_batch_time
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.deadline_multiplier
        == config_from_pickle.scheduler_config.native_handle.deadline_multiplier
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_deadline
        == config_from_pickle.scheduler_config.native_handle.min_deadline
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
        == config_from_pickle.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
    )
    assert config.metrics_config == config_from_pickle.metrics_config


@pytest.mark.parametrize(
    "model_config, worker_config, cache_config, parallel_config, scheduler_config, metrics_config",
    [
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(block_size=32, num_gpu_blocks=1024),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
    ],
)
@pytest.mark.unit
def test_llm_replica_controller_config_creation(
    model_config,
    worker_config,
    cache_config,
    parallel_config,
    scheduler_config,
    metrics_config,
):
    """Tests creating valid LlmReplicaControllerConfig objects and accessing their properties."""
    config = LlmReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        scheduler_config=scheduler_config,
        metrics_config=metrics_config,
    )
    assert config.model_config == model_config
    assert config.worker_config == worker_config
    assert config.cache_config == cache_config
    assert config.parallel_config == parallel_config
    assert config.scheduler_config == scheduler_config
    assert config.metrics_config == metrics_config

    assert config.native_handle is not None  # pyright: ignore

    assert config.get_type() == ReplicaControllerType.LLM_BASE


@pytest.mark.parametrize(
    "model_config, worker_config, cache_config, parallel_config, scheduler_config, metrics_config",
    [
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(block_size=32, num_gpu_blocks=1024),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
    ],
)
@pytest.mark.unit
def test_can_deep_copy_llm_replica_controller_config(
    model_config,
    worker_config,
    cache_config,
    parallel_config,
    scheduler_config,
    metrics_config,
):
    """Tests deep copying valid LlmReplicaControllerConfig objects and accessing their properties."""
    config = LlmReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        scheduler_config=scheduler_config,
        metrics_config=metrics_config,
    )

    config_deep_copy = copy.deepcopy(config)

    assert config.model_config == config_deep_copy.model_config
    assert config.worker_config == config_deep_copy.worker_config
    assert config.cache_config == config_deep_copy.cache_config
    assert config.parallel_config == config_deep_copy.parallel_config
    assert (
        compare_attributes(config.scheduler_config, config_deep_copy.scheduler_config)
        == True
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_batch_size
        == config_deep_copy.scheduler_config.native_handle.max_batch_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_chunk_size
        == config_deep_copy.scheduler_config.native_handle.max_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_chunk_size
        == config_deep_copy.scheduler_config.native_handle.min_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.target_batch_time
        == config_deep_copy.scheduler_config.native_handle.target_batch_time
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.deadline_multiplier
        == config_deep_copy.scheduler_config.native_handle.deadline_multiplier
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_deadline
        == config_deep_copy.scheduler_config.native_handle.min_deadline
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_deep_copy.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
        == config_deep_copy.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
    )
    assert config.metrics_config == config_deep_copy.metrics_config

    assert config is not config_deep_copy


@pytest.mark.parametrize(
    "model_config, worker_config, cache_config, parallel_config, scheduler_config, metrics_config",
    [
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
        (
            ModelConfig(),
            WorkerConfig(),
            CacheConfig(block_size=32, num_gpu_blocks=1024),
            ParallelConfig(),
            StReplicaSchedulerConfig(),
            MetricsConfig(),
        ),
    ],
)
@pytest.mark.unit
def test_can_pickle_llm_replica_controller_config(
    model_config,
    worker_config,
    cache_config,
    parallel_config,
    scheduler_config,
    metrics_config,
):
    """Tests pickling LlmReplicaControllerConfig objects and accessing their properties."""
    config = LlmReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        scheduler_config=scheduler_config,
        metrics_config=metrics_config,
    )

    pickled_config = pickle.dumps(config)
    config_from_pickle = pickle.loads(pickled_config)

    assert config.model_config == config_from_pickle.model_config
    assert config.worker_config == config_from_pickle.worker_config
    assert config.cache_config == config_from_pickle.cache_config
    assert config.parallel_config == config_from_pickle.parallel_config
    assert (
        compare_attributes(config.scheduler_config, config_from_pickle.scheduler_config)
        == True
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_batch_size
        == config_from_pickle.scheduler_config.native_handle.max_batch_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.max_chunk_size
        == config_from_pickle.scheduler_config.native_handle.max_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_chunk_size
        == config_from_pickle.scheduler_config.native_handle.min_chunk_size
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.target_batch_time
        == config_from_pickle.scheduler_config.native_handle.target_batch_time
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.deadline_multiplier
        == config_from_pickle.scheduler_config.native_handle.deadline_multiplier
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.min_deadline
        == config_from_pickle.scheduler_config.native_handle.min_deadline
    )
    assert (
        config.scheduler_config.native_handle is not None
        and config_from_pickle.scheduler_config.native_handle is not None
        and config.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
        == config_from_pickle.scheduler_config.native_handle.long_seq_kv_cache_len_threshold
    )
    assert config.metrics_config == config_from_pickle.metrics_config


@pytest.mark.parametrize(
    "num_replicas, num_tokenizer_workers",
    [(1, 5), (2, 10), (4, 20)],
)
@pytest.mark.unit
def test_llm_replicaset_controller_config_creation(num_replicas, num_tokenizer_workers):
    """Tests creating valid LlmReplicasetControllerConfig objects and accessing their properties."""
    cache_config = CacheConfig(block_size=32, num_gpu_blocks=1024)
    model_config = ModelConfig()
    worker_config = WorkerConfig()
    parallel_config = ParallelConfig()
    metrics_config = MetricsConfig()

    replica_controller_config = LlmReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        metrics_config=metrics_config,
    )

    scheduler_config = PullReplicasetSchedulerConfig()

    replicaset_config = LlmReplicasetControllerConfig(
        num_replicas=num_replicas,
        replica_controller_config=replica_controller_config,
        replicaset_scheduler_config=scheduler_config,
        num_tokenizer_workers=num_tokenizer_workers,
    )

    assert replicaset_config.num_replicas == num_replicas
    assert replicaset_config.num_tokenizer_workers == num_tokenizer_workers

    native_handle = replicaset_config.native_handle  # pyright: ignore
    assert native_handle.num_replicas == num_replicas
    assert native_handle.num_tokenizer_workers == num_tokenizer_workers


@pytest.mark.parametrize(
    "num_replicas, num_tokenizer_workers",
    [(1, 5), (2, 10), (4, 20)],
)
@pytest.mark.unit
def test_can_deep_copy_llm_replicaset_controller_config(
    num_replicas, num_tokenizer_workers
):
    """Tests deep copying LlmReplicasetControllerConfig objects and accessing their properties."""
    # Create a custom replica controller config
    cache_config = CacheConfig(block_size=32, num_gpu_blocks=1024)
    model_config = ModelConfig()
    worker_config = WorkerConfig()
    parallel_config = ParallelConfig()
    metrics_config = MetricsConfig()

    replica_controller_config = LlmReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        metrics_config=metrics_config,
    )

    scheduler_config = PullReplicasetSchedulerConfig()

    replicaset_config = LlmReplicasetControllerConfig(
        num_replicas=num_replicas,
        replica_controller_config=replica_controller_config,
        replicaset_scheduler_config=scheduler_config,
        num_tokenizer_workers=num_tokenizer_workers,
    )

    replicaset_config_deep_copy = copy.deepcopy(replicaset_config)

    assert replicaset_config_deep_copy.num_replicas == num_replicas
    assert replicaset_config_deep_copy.num_tokenizer_workers == num_tokenizer_workers

    assert replicaset_config_deep_copy is not replicaset_config
    assert (
        replicaset_config_deep_copy.replica_controller_config
        is not replicaset_config.replica_controller_config
    )
    assert (
        replicaset_config_deep_copy.replica_controller_config.cache_config
        is not replicaset_config.replica_controller_config.cache_config
    )


@pytest.mark.parametrize(
    "num_replicas, num_tokenizer_workers",
    [(1, 5), (2, 10), (4, 20)],
)
@pytest.mark.unit
def test_can_pickle_llm_replicaset_controller_config(
    num_replicas, num_tokenizer_workers
):
    """Tests pickling LlmReplicasetControllerConfig objects and accessing their properties."""
    cache_config = CacheConfig(block_size=32, num_gpu_blocks=1024)
    model_config = ModelConfig()
    worker_config = WorkerConfig()
    parallel_config = ParallelConfig()
    metrics_config = MetricsConfig()

    replica_controller_config = LlmReplicaControllerConfig(
        model_config=model_config,
        worker_config=worker_config,
        cache_config=cache_config,
        parallel_config=parallel_config,
        metrics_config=metrics_config,
    )

    scheduler_config = PullReplicasetSchedulerConfig()

    replicaset_config = LlmReplicasetControllerConfig(
        num_replicas=num_replicas,
        replica_controller_config=replica_controller_config,
        replicaset_scheduler_config=scheduler_config,
        num_tokenizer_workers=num_tokenizer_workers,
    )

    pickled_config = pickle.dumps(replicaset_config)
    replicaset_config_from_pickle = pickle.loads(pickled_config)

    assert replicaset_config_from_pickle.num_replicas == num_replicas
    assert replicaset_config_from_pickle.num_tokenizer_workers == num_tokenizer_workers

    assert replicaset_config_from_pickle is not replicaset_config
    assert (
        replicaset_config_from_pickle.replica_controller_config
        is not replicaset_config.replica_controller_config
    )
