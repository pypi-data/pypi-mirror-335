from typing import Dict, List, Tuple

import ray

from vajra.logger import init_logger
from vajra.utils import get_ip

logger = init_logger(__name__)


class ResourceAllocator:
    """Handles GPU resource allocation for replicas"""

    def __init__(self) -> None:
        self._init_ray()

    def _init_ray(self):
        ray.init(ignore_reinit_error=True)

    def validate_cluster_resources(self, num_replicas: int, world_size: int) -> None:
        """Validate that cluster has sufficient GPU resources"""
        num_gpus_required = num_replicas * world_size
        available_resources = ray.available_resources()

        assert (
            available_resources["GPU"] >= num_gpus_required
        ), f"Insufficient GPUs. Required: {num_gpus_required}, Available: {available_resources['GPU']}"

    def get_replica_resources(self, world_size: int) -> List[Tuple[str, int]]:
        """Generate resource allocation for a single replica
        Args:
            world_size: Number of GPUs needed for this replica
        Returns:
            List of (node_ip, device_id) tuples for the replica
        """
        # First validate total resources needed
        self.validate_cluster_resources(1, world_size)  # Only 1 replica

        cluster_resources_keys = list(ray.available_resources().keys())
        num_gpus = ray.available_resources()["GPU"]
        ip_addresses = [
            x
            for x in cluster_resources_keys
            if x.startswith("node:") and x != "node:__internal_head__"
        ]

        runner_ip = f"node:{get_ip()}"
        if runner_ip in ip_addresses:
            ip_addresses.remove(runner_ip)
        ip_addresses.insert(0, runner_ip)

        num_nodes = len(ip_addresses)
        assert num_nodes > 0, "No nodes found in the cluster"
        assert num_gpus > 0, "No GPUs found in the cluster"
        assert (
            num_gpus % num_nodes == 0
        ), f"Number of GPUs ({num_gpus}) is not divisible by number of nodes ({num_nodes})"

        num_gpus_per_node = int(num_gpus // num_nodes)

        assert num_gpus >= world_size, (
            f"Insufficient GPUs. Required: {world_size}, " f"Available: {num_gpus}"
        )

        # Get first available GPUs across nodes
        devices: List[Tuple[str, int]] = []
        gpu_count = 0
        for ip_address in ip_addresses:
            for gpu_id in reversed(range(num_gpus_per_node)):
                devices.append((ip_address, gpu_id))
                gpu_count += 1
                if gpu_count >= world_size:
                    break
            if gpu_count >= world_size:
                break

        return devices[:world_size]

    def get_replicaset_resource_mapping(
        self, num_replicas: int, world_size: int
    ) -> Dict[int, List[Tuple[str, int]]]:
        """Generate resource allocation mapping for all replicas
        Args:
            num_replicas: Number of replicas to allocate resources for
            world_size: Number of GPUs needed per replica
        Returns:
            Dict mapping replica IDs to lists of (node_ip, device_id) tuples
        """
        # First validate total resources needed
        self.validate_cluster_resources(num_replicas, world_size)

        # Get all available GPUs first to ensure fair distribution
        cluster_resources_keys = list(ray.available_resources().keys())
        ip_addresses = [
            x
            for x in cluster_resources_keys
            if x.startswith("node:") and x != "node:__internal_head__"
        ]

        runner_ip = f"node:{get_ip()}"
        if runner_ip in ip_addresses:
            ip_addresses.remove(runner_ip)
        ip_addresses.insert(0, runner_ip)

        # Pre-allocate all GPUs to ensure fair distribution across replicas
        available_gpus: List[Tuple[str, int]] = []
        for ip_address in ip_addresses:
            num_gpus_per_node = int(
                ray.available_resources()["GPU"] // len(ip_addresses)
            )
            for gpu_id in reversed(range(num_gpus_per_node)):
                available_gpus.append((ip_address, gpu_id))

        # Allocate resources for each replica
        resources = {}
        for replica_id in range(num_replicas):
            devices = [available_gpus.pop(0) for _ in range(world_size)]
            resources[replica_id] = devices

        return resources
