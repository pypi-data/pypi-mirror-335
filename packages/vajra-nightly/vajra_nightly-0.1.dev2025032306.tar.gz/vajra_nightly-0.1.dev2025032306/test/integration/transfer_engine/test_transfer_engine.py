import os

import pytest
import torch
import torch.distributed
import torch.multiprocessing

from vajra._native.configs import ReplicaResourceConfig, TransferEngineConfig
from vajra._native.enums import TransferBackendType
from vajra._native.transfer_engine.interface import (
    BaseTransferEngine,
)
from vajra.config import ModelConfig, ParallelConfig


@pytest.fixture(scope="module")
def model_config():
    model_config = ModelConfig(
        model="meta-llama/Meta-Llama-3-8B", override_num_layers=12
    )
    return model_config


@pytest.fixture(scope="module")
def parallel_config():
    parallel_config = ParallelConfig(
        pipeline_parallel_size=1,
        tensor_parallel_size=1,
        kv_parallel_size=1,
        enable_sequence_pipeline_parallel=False,
        enable_chunked_pipeline_comm_opt=False,
    )
    return parallel_config


@pytest.fixture(scope="module")
def pipeline_parallel_config():
    parallel_config = ParallelConfig(
        pipeline_parallel_size=2,
        tensor_parallel_size=1,
        kv_parallel_size=1,
        enable_sequence_pipeline_parallel=False,
        enable_chunked_pipeline_comm_opt=False,
    )
    return parallel_config


@pytest.fixture(scope="module")
def tp_parallel_config():
    parallel_config = ParallelConfig(
        pipeline_parallel_size=1,
        tensor_parallel_size=2,
        kv_parallel_size=1,
        enable_sequence_pipeline_parallel=False,
        enable_chunked_pipeline_comm_opt=False,
    )
    return parallel_config


def create_replica_resource_config(parallel_config, model_config):
    return ReplicaResourceConfig(
        parallel_config.native_handle, model_config.native_handle
    )


def create_transfer_engine(
    transfer_backend_type, global_rank, replica_resource_mapping, world_group
):
    transfer_engine_config = TransferEngineConfig(
        transfer_backend_type,
        global_rank,
        replica_resource_mapping,
        world_group,
    )
    transfer_engine = BaseTransferEngine.create_from(transfer_engine_config)
    return transfer_engine


def run_transfer_engine_test(
    rank,
    world_size,
    num_replicas,
    send_replica_id,
    recv_replica_id,
    send_ranks,
    recv_ranks,
    send_page_list,
    recv_page_list,
    pp_list,
    tp_list,
    layer_id,
    parallel_config,
    pipeline_parallel_config,
    tp_parallel_config,
    model_config,
):
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    torch.distributed.init_process_group("nccl", rank=rank, world_size=world_size)
    world_group = torch.distributed.group.WORLD

    replica_resource_mapping = []
    replica_id = -1
    seen_num_gpus = 0
    for i in range(num_replicas):
        current_parallel_config = parallel_config
        if pp_list[i]:
            current_parallel_config = pipeline_parallel_config
        elif tp_list[i]:
            current_parallel_config = tp_parallel_config
        replica_resource_config = create_replica_resource_config(
            current_parallel_config, model_config
        )
        replica_resource_mapping.append(replica_resource_config)
        seen_num_gpus += current_parallel_config.world_size
        if replica_id == -1 and seen_num_gpus > rank:
            replica_id = i

    transfer_engine = create_transfer_engine(
        TransferBackendType.TORCH, rank, replica_resource_mapping, world_group
    )
    num_pages = 8
    page_size = 16
    num_heads = 8
    head_dim = 128
    head_dim = head_dim // 2 if tp_list[replica_id] else head_dim
    device = torch.device(f"cuda:{rank}")
    send_tensor = torch.zeros(num_pages, 1, page_size, num_heads, head_dim).to(device)
    for i in range(num_pages):
        send_tensor[i, :] = i
    recv_tensor = torch.zeros(num_pages, 1, page_size, num_heads, head_dim).to(device)

    if rank in send_ranks:
        work = transfer_engine.async_send(
            dst_replica_id=recv_replica_id,
            page_tensor=send_tensor,
            page_list=send_page_list,
            layer_id=layer_id,
        )
        work.synchronize()
    elif rank in recv_ranks:
        work = transfer_engine.async_recv(
            src_replica_id=send_replica_id,
            page_tensor=recv_tensor,
            page_list=recv_page_list,
            layer_id=layer_id,
        )
        work.synchronize()

    torch.distributed.barrier()
    send_page_list_tensor = torch.tensor(send_page_list)
    recv_page_list_tensor = torch.tensor(recv_page_list)

    if rank in recv_ranks:
        assert torch.allclose(
            send_tensor[send_page_list_tensor], recv_tensor[recv_page_list_tensor]
        )

    torch.distributed.destroy_process_group()


@pytest.mark.integration
@pytest.mark.gpu
@pytest.mark.parametrize(
    "world_size, num_replicas, send_replica_id, recv_replica_id, send_ranks, recv_ranks, send_page_list, recv_page_list, pp_list, tp_list, layer_id",
    [
        # -- Tests with different page rank/configurations --
        (2, 2, 0, 1, {0}, {1}, [0, 1, 7], [0, 1, 7], [False, False], [False, False], 0),
        (
            2,
            2,
            0,
            1,
            {0},
            {1},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False],
            [False, False],
            0,
        ),
        (
            2,
            2,
            0,
            1,
            {0},
            {1},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False],
            [False, False],
            0,
        ),
        (
            2,
            2,
            0,
            1,
            {0},
            {1},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False],
            [False, False],
            0,
        ),
        (
            2,
            2,
            1,
            0,
            {1},
            {0},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False],
            [False, False],
            0,
        ),
        (
            4,
            4,
            1,
            0,
            {1},
            {0},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            2,
            1,
            {2},
            {1},
            [0, 1, 6, 7],
            [0, 1, 2, 7],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            2,
            3,
            {2},
            {3},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            2,
            0,
            {2},
            {0},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            3,
            2,
            {3},
            {2},
            [0, 1, 2, 3, 4, 5, 6, 7],
            [0, 1, 2, 3, 4, 5, 6, 7],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            3,
            1,
            {3},
            {1},
            [6, 7],
            [6, 7],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            3,
            0,
            {3},
            {0},
            [0, 1],
            [0, 1],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        (
            4,
            4,
            0,
            3,
            {0},
            {3},
            [0, 1, 2],
            [0, 1, 3],
            [False, False, False, False],
            [False, False, False, False],
            0,
        ),
        # -- Tests with tensor parallelism --
        (4, 2, 0, 1, {0}, {2}, [0, 1, 2], [0, 1, 3], [False, False], [True, True], 10),
        (4, 2, 0, 1, {1}, {3}, [0, 1, 2], [0, 1, 3], [False, False], [True, True], 10),
        (
            3,
            2,
            0,
            1,
            {0, 1},
            {2},
            [0, 1, 2],
            [0, 1, 3],
            [False, False],
            [True, False],
            10,
        ),
        (
            3,
            2,
            0,
            1,
            {0},
            {1, 2},
            [0, 1, 2],
            [0, 1, 3],
            [False, False],
            [False, True],
            10,
        ),
        # -- Tests with pipeline parallelism --
        (3, 2, 1, 0, {2}, {1}, [0, 1, 2], [0, 1, 3], [True, False], [False, False], 10),
        (3, 2, 1, 0, {2}, {0}, [0, 1, 2], [0, 1, 3], [True, False], [False, False], 2),
        (3, 2, 0, 1, {1}, {2}, [0, 1, 2], [0, 1, 3], [True, False], [False, False], 11),
        (3, 2, 0, 1, {0}, {2}, [0, 1, 2], [0, 1, 3], [True, False], [False, False], 1),
        (3, 2, 0, 1, {0}, {1}, [0, 1, 2], [0, 1, 3], [False, True], [False, False], 0),
        (3, 2, 0, 1, {0}, {2}, [0, 1, 2], [0, 1, 3], [False, True], [False, False], 9),
        (4, 2, 0, 1, {0}, {2}, [0, 1, 2], [0, 1, 3], [True, True], [False, False], 4),
        (4, 2, 0, 1, {1}, {3}, [0, 1, 2], [0, 1, 3], [True, True], [False, False], 8),
    ],
)
def test_integration_send_recv(
    world_size,
    num_replicas,
    send_replica_id,
    recv_replica_id,
    send_ranks,
    recv_ranks,
    send_page_list,
    recv_page_list,
    pp_list,
    tp_list,
    layer_id,
    parallel_config,
    pipeline_parallel_config,
    tp_parallel_config,
    model_config,
):
    """Tests sends and receives between replicas with world size 1.
    Parameterize must have correct send and recv rank and send and recv replica ids.
    It is not calculated automatically
    (for the integration test frontend, but the transfer engine does do that)"""
    torch.multiprocessing.spawn(  # type: ignore
        run_transfer_engine_test,
        args=(
            world_size,
            num_replicas,
            send_replica_id,
            recv_replica_id,
            send_ranks,
            recv_ranks,
            send_page_list,
            recv_page_list,
            pp_list,
            tp_list,
            layer_id,
            parallel_config,
            pipeline_parallel_config,
            tp_parallel_config,
            model_config,
        ),
        nprocs=world_size,
        join=True,
    )
