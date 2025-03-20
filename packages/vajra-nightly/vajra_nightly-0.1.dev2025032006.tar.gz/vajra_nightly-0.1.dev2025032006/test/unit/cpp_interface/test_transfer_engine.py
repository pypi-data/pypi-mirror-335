import pytest
import torch.distributed

from vajra._native.configs import ReplicaResourceConfig, TransferEngineConfig
from vajra._native.transfer_engine import (
    TransferBackendType,
    TransferEngine,
)
from vajra.config import ModelConfig, ParallelConfig


@pytest.mark.unit
def test_can_create_transfer_engine():
    """Tests can create a Transfer Engine."""

    model_config = ModelConfig(
        model="meta-llama/Meta-Llama-3-8B", override_num_layers=12
    )
    model_config_c = model_config.native_handle
    parallel_config = ParallelConfig(
        pipeline_parallel_size=1,
        tensor_parallel_size=1,
        kv_parallel_size=1,
        enable_sequence_pipeline_parallel=False,
        enable_chunked_pipeline_comm_opt=False,
    )
    parallel_config_c = parallel_config.native_handle
    replica_resource_mapping = [
        ReplicaResourceConfig(parallel_config_c, model_config_c)
    ]
    global_rank = 0

    transfer_engine_config = TransferEngineConfig(
        TransferBackendType.TORCH,
        global_rank,
        replica_resource_mapping,
        torch.distributed.group.WORLD,
    )
    transfer_engine = TransferEngine.create_from(transfer_engine_config)
    assert transfer_engine is not None
