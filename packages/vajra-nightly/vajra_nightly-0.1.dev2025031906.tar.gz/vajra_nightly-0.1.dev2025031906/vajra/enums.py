from enum import Enum


class ReplicasetSchedulerType(Enum):
    PULL = "PULL"
    ROUND_ROBIN = "ROUND_ROBIN"


class ReplicasetControllerType(Enum):
    LLM = "LLM"


class ReplicaControllerType(Enum):
    LLM_BASE = "LLM_BASE"
    LLM_PIPELINE_PARALLEL = "LLM_PIPELINE_PARALLEL"


class SchedulerType(Enum):
    FCFS_FIXED_CHUNK = "FCFS_FIXED_CHUNK"
    FCFS = "FCFS"
    EDF = "EDF"
    LRS = "LRS"
    ST = "ST"


class RequestGeneratorType(Enum):
    SYNTHETIC = "SYNTHETIC"
    TRACE = "TRACE"


class RequestIntervalGeneratorType(Enum):
    POISSON = "POISSON"
    GAMMA = "GAMMA"
    STATIC = "STATIC"
    TRACE = "TRACE"


class RequestLengthGeneratorType(Enum):
    UNIFORM = "UNIFORM"
    ZIPF = "ZIPF"
    TRACE = "TRACE"
    FIXED = "FIXED"
