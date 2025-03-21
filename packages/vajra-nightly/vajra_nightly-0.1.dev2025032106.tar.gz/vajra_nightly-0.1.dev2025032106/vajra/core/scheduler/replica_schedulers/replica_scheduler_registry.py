from vajra.core.scheduler.replica_schedulers.edf_replica_scheduler import (
    EdfReplicaScheduler,
)
from vajra.core.scheduler.replica_schedulers.fcfs_fixed_chunk_replica_scheduler import (
    FcfsFixedChunkReplicaScheduler,
)
from vajra.core.scheduler.replica_schedulers.fcfs_replica_scheduler import (
    FcfsReplicaScheduler,
)
from vajra.core.scheduler.replica_schedulers.lrs_replica_scheduler import (
    LrsReplicaScheduler,
)
from vajra.core.scheduler.replica_schedulers.st_replica_scheduler import (
    StReplicaScheduler,
)
from vajra.enums import SchedulerType
from vajra.utils.base_registry import BaseRegistry


class ReplicaSchedulerRegistry(BaseRegistry):
    pass


ReplicaSchedulerRegistry.register(
    SchedulerType.FCFS_FIXED_CHUNK, FcfsFixedChunkReplicaScheduler
)
ReplicaSchedulerRegistry.register(SchedulerType.FCFS, FcfsReplicaScheduler)
ReplicaSchedulerRegistry.register(SchedulerType.EDF, EdfReplicaScheduler)
ReplicaSchedulerRegistry.register(SchedulerType.LRS, LrsReplicaScheduler)
ReplicaSchedulerRegistry.register(SchedulerType.ST, StReplicaScheduler)
