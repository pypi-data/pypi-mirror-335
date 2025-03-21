from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from vajra._native.configs import BaseEndpointConfig as BaseEndpointConfig_C
from vajra._native.configs import (
    BaseReplicaControllerConfig as BaseReplicaControllerConfig_C,
)
from vajra._native.configs import (
    BaseReplicaSchedulerConfig as BaseReplicaSchedulerConfig_C,
)
from vajra._native.configs import (
    BaseReplicasetControllerConfig as BaseReplicasetControllerConfig_C,
)
from vajra._native.configs import CacheConfig as CacheConfig_C
from vajra._native.configs import (
    EdfReplicaSchedulerConfig as EdfReplicaSchedulerConfig_C,
)
from vajra._native.configs import (
    FcfsFixedChunkReplicaSchedulerConfig as FcfsFixedChunkReplicaSchedulerConfig_C,
)
from vajra._native.configs import (
    FcfsReplicaSchedulerConfig as FcfsReplicaSchedulerConfig_C,
)
from vajra._native.configs import InferenceEngineConfig as InferenceEngineConfig_C
from vajra._native.configs import (
    LlmReplicaControllerConfig as LlmReplicaControllerConfig_C,
)
from vajra._native.configs import (
    LlmReplicasetControllerConfig as LlmReplicasetControllerConfig_C,
)
from vajra._native.configs import (
    LrsReplicaSchedulerConfig as LrsReplicaSchedulerConfig_C,
)
from vajra._native.configs import MetricsConfig as MetricsConfig_C
from vajra._native.configs import ModelConfig as ModelConfig_C
from vajra._native.configs import ParallelConfig as ParallelConfig_C
from vajra._native.configs import (
    PullReplicasetSchedulerConfig as PullReplicasetSchedulerConfig_C,
)
from vajra._native.configs import (
    RoundRobinReplicasetSchedulerConfig as RoundRobinReplicasetSchedulerConfig_C,
)
from vajra._native.configs import StReplicaSchedulerConfig as StReplicaSchedulerConfig_C
from vajra._native.configs import WorkerConfig as WorkerConfig_C
from vajra.config.base_poly_config import BasePolyConfig
from vajra.config.flat_dataclass import create_flat_dataclass
from vajra.enums import (
    ReplicaControllerType,
    ReplicasetControllerType,
    ReplicasetSchedulerType,
    SchedulerType,
)
from vajra.logger import init_logger
from vajra.transformers_utils.config import get_config
from vajra.utils.hf_utils import get_and_verify_dtype, get_and_verify_max_len

logger = init_logger(__name__)


@dataclass
class ModelConfig:
    model: str = field(
        default="meta-llama/Meta-Llama-3-8B-Instruct",
        metadata={"help": "Name or path of the huggingface model to use."},
    )
    trust_remote_code: bool = field(
        default=True,
        metadata={
            "help": "Trust remote code (e.g., from HuggingFace) when downloading the model and tokenizer."
        },
    )
    download_dir: Optional[str] = field(
        default=None,
        metadata={
            "help": "Directory to download and load the weights, default to the default cache directory of huggingface."
        },
    )
    load_format: str = field(
        default="auto",
        metadata={
            "help": "The format of the model weights to load: 'auto', 'pt', 'safetensors', 'npcache', or 'dummy'."
        },
    )
    dtype: str = field(
        default="float16",
        metadata={
            "help": "Data type for model weights and activations. 'auto' will use FP16 for FP32 and FP16 models, and BF16 for BF16 models."
        },
    )
    seed: int = field(default=0, metadata={"help": "Random seed for reproducibility."})
    revision: Optional[str] = field(
        default=None,
        metadata={
            "help": "The specific model version to use. Can be a branch name, tag name, or commit id."
        },
    )
    max_model_len: int = field(
        default=-1,
        metadata={
            "help": "Maximum length of a sequence (including prompt and output). If None, will be derived from the model."
        },
    )
    override_num_layers: Optional[int] = field(
        default=None,
        metadata={
            "help": "Override the number of layers in the model. If None, will be derived from the model."
        },
    )

    def __post_init__(self):
        self.hf_config = get_config(self.model, self.trust_remote_code, self.revision)

        if self.override_num_layers is not None:
            self.hf_config.num_hidden_layers = self.override_num_layers

        self.torch_dtype = get_and_verify_dtype(self.hf_config, self.dtype)
        self.hf_config.dtype = self.torch_dtype
        self.max_model_len = get_and_verify_max_len(self.hf_config, self.max_model_len)
        self._verify_load_format()
        self.native_handle = ModelConfig_C(
            self.model,
            self.trust_remote_code,
            self.download_dir,
            self.load_format,
            self.dtype,
            self.seed,
            self.revision,
            self.max_model_len,
            self.get_total_num_layers(),
        )

    def _verify_load_format(self) -> None:
        load_format = self.load_format.lower()
        if load_format not in ["auto", "pt", "safetensors", "npcache", "dummy"]:
            raise ValueError(
                f"Unknown load format: {self.load_format}. Must be one of "
                "'auto', 'pt', 'safetensors', 'npcache', or 'dummy'."
            )
        self.load_format = load_format

    def verify_with_parallel_config(
        self,
        parallel_config: "ParallelConfig",
    ) -> None:
        total_num_attention_heads = self.hf_config.num_attention_heads
        tensor_parallel_size = parallel_config.tensor_parallel_size
        if total_num_attention_heads % tensor_parallel_size != 0:
            raise ValueError(
                f"Total number of attention heads ({total_num_attention_heads})"
                " must be divisible by tensor parallel size "
                f"({tensor_parallel_size})."
            )

        total_num_hidden_layers = self.hf_config.num_hidden_layers
        pipeline_parallel_size = parallel_config.pipeline_parallel_size
        if total_num_hidden_layers % pipeline_parallel_size != 0:
            raise ValueError(
                f"Total number of hidden layers ({total_num_hidden_layers}) "
                "must be divisible by pipeline parallel size "
                f"({pipeline_parallel_size})."
            )

    def get_hidden_size(self) -> int:
        return self.hf_config.hidden_size

    def get_head_size(self) -> int:
        # FIXME(woosuk): This may not be true for all models.
        return self.hf_config.hidden_size // self.hf_config.num_attention_heads

    def get_num_kv_heads(self, parallel_config: "ParallelConfig") -> int:
        # For LLaMA-2:
        if getattr(self.hf_config, "num_key_value_heads", None) is not None:
            return (
                self.hf_config.num_key_value_heads
                // parallel_config.tensor_parallel_size
            )
        total_num_attention_heads = self.hf_config.num_attention_heads
        return total_num_attention_heads // parallel_config.tensor_parallel_size

    def get_num_q_heads(self, parallel_config: "ParallelConfig") -> int:
        if getattr(self.hf_config, "num_attention_heads", None) is not None:
            return (
                self.hf_config.num_attention_heads
                // parallel_config.tensor_parallel_size
            )
        raise ValueError("num_attention_heads is not defined in the model config")

    def get_num_layers(self, parallel_config: "ParallelConfig") -> int:
        total_num_hidden_layers = self.hf_config.num_hidden_layers
        return total_num_hidden_layers // parallel_config.pipeline_parallel_size

    def get_total_num_layers(self) -> int:
        return self.hf_config.num_hidden_layers


@dataclass
class CacheConfig:
    block_size: int = field(
        default=16, metadata={"help": "Size of a cache block in number of tokens."}
    )
    num_gpu_blocks: Optional[int] = field(
        default=0,
        metadata={
            "help": "Number of GPU blocks for caching. This gets set after profiling."
        },
    )

    def set_num_gpu_blocks(self, num_gpu_blocks: int):
        self.num_gpu_blocks = num_gpu_blocks
        self.native_handle = CacheConfig_C(
            self.block_size,
            self.num_gpu_blocks,
        )

    def __post_init__(self):
        # Create native handler
        self.native_handle = CacheConfig_C(
            self.block_size,
            self.num_gpu_blocks,
        )


@dataclass
class ParallelConfig:
    pipeline_parallel_size: int = field(
        default=1, metadata={"help": "Number of pipeline parallel groups."}
    )
    tensor_parallel_size: int = field(
        default=1, metadata={"help": "Number of tensor parallel groups."}
    )
    enable_expert_parallel: bool = field(
        default=False, metadata={"help": "Enable expert parallelism."}
    )
    enable_sequence_pipeline_parallel: bool = field(
        default=False, metadata={"help": "Enable sequence pipeline parallelism."}
    )
    enable_chunked_pipeline_comm_opt: bool = field(
        default=True,
        metadata={
            "help": "Enable pipeline parallel communication optimization in pipeline stages."
        },
    )
    kv_parallel_size: int = field(
        default=1, metadata={"help": "Number of cache parallel groups."}
    )
    max_num_tokens_per_kvp_group: int = field(
        default=1024 * 1024,
        metadata={
            "help": "Maximum number of tokens per sequence that can be stored in the cache parallel group."
        },
    )

    def __post_init__(self):
        if self.enable_sequence_pipeline_parallel and self.pipeline_parallel_size == 1:
            logger.warning(
                "Sequence pipeline parallelism is enabled but pipeline_parallel_size is 1."
            )
            self.enable_sequence_pipeline_parallel = False

        if self.enable_chunked_pipeline_comm_opt and not (
            self.pipeline_parallel_size > 1 and self.tensor_parallel_size > 1
        ):
            logger.warning(
                "Chunked pipeline communication optimization is enabled but pipeline_parallel_size or tensor_parallel_size is not greater than 1."
            )
            self.enable_chunked_pipeline_comm_opt = False

        self.world_size = (
            self.pipeline_parallel_size
            * self.tensor_parallel_size
            * self.kv_parallel_size
        )
        self.native_handle = ParallelConfig_C(
            self.pipeline_parallel_size,
            self.tensor_parallel_size,
            self.enable_expert_parallel,
            self.enable_sequence_pipeline_parallel,
            self.enable_chunked_pipeline_comm_opt,
            self.kv_parallel_size,
            self.max_num_tokens_per_kvp_group,
        )


@dataclass(frozen=True)
class BaseReplicasetSchedulerConfig(BasePolyConfig):
    pass


@dataclass(frozen=True)
class PullReplicasetSchedulerConfig(BaseReplicasetSchedulerConfig):
    @staticmethod
    def get_type():
        return ReplicasetSchedulerType.PULL

    def __post_init__(self):
        object.__setattr__(self, "native_handle", PullReplicasetSchedulerConfig_C())


@dataclass(frozen=True)
class RoundRobinReplicasetSchedulerConfig(BaseReplicasetSchedulerConfig):
    @staticmethod
    def get_type():
        return ReplicasetSchedulerType.ROUND_ROBIN

    def __post_init__(self):
        object.__setattr__(
            self, "native_handle", RoundRobinReplicasetSchedulerConfig_C()
        )


@dataclass(frozen=True)
class BaseReplicaSchedulerConfig(BasePolyConfig):
    max_batch_size: int = field(
        default=128,
        metadata={
            "help": "Maximum number of sequences to be processed in a single iteration (batch size)."
        },
    )
    native_handle: Optional[Any] = None

    @abstractmethod
    def get_max_num_batched_tokens(self):
        raise NotImplementedError

    def __post_init__(self):
        object.__setattr__(
            self, "native_handle", BaseReplicaSchedulerConfig_C(self.max_batch_size)
        )


@dataclass(frozen=True)
class FcfsFixedChunkReplicaSchedulerConfig(BaseReplicaSchedulerConfig):
    chunk_size: int = field(
        default=2048,
        metadata={"help": "Chunk size for Vajra."},
    )

    def get_max_num_batched_tokens(self):
        return self.chunk_size

    @staticmethod
    def get_type():
        return SchedulerType.FCFS_FIXED_CHUNK

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(
            self,
            "native_handle",
            FcfsFixedChunkReplicaSchedulerConfig_C(
                self.max_batch_size, self.chunk_size
            ),
        )


@dataclass(frozen=True)
class FcfsReplicaSchedulerConfig(BaseReplicaSchedulerConfig):
    max_chunk_size: int = field(
        default=8192,
        metadata={"help": "Maximum chunk size."},
    )
    min_chunk_size: int = field(
        default=32,
        metadata={"help": "Minimum chunk size."},
    )
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for FCFS."},
    )

    def get_max_num_batched_tokens(self):
        return self.max_chunk_size

    @staticmethod
    def get_type():
        return SchedulerType.FCFS

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(
            self,
            "native_handle",
            FcfsReplicaSchedulerConfig_C(
                self.max_batch_size,
                self.max_chunk_size,
                self.min_chunk_size,
                self.target_batch_time,
            ),
        )


@dataclass(frozen=True)
class EdfReplicaSchedulerConfig(BaseReplicaSchedulerConfig):
    max_chunk_size: int = field(
        default=8192,
        metadata={"help": "Maximum chunk size."},
    )
    min_chunk_size: int = field(
        default=32,
        metadata={"help": "Minimum chunk size."},
    )
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for EDF."},
    )
    deadline_multiplier: float = field(
        default=1.5,
        metadata={"help": "Deadline multiplier for EDF."},
    )
    min_deadline: float = field(
        default=0.5,
        metadata={"help": "Minimum deadline for EDF."},
    )

    def get_max_num_batched_tokens(self):
        return self.max_chunk_size

    @staticmethod
    def get_type():
        return SchedulerType.EDF

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(
            self,
            "native_handle",
            EdfReplicaSchedulerConfig_C(
                self.max_batch_size,
                self.max_chunk_size,
                self.min_chunk_size,
                self.target_batch_time,
                self.deadline_multiplier,
                self.min_deadline,
            ),
        )


@dataclass(frozen=True)
class LrsReplicaSchedulerConfig(BaseReplicaSchedulerConfig):
    max_chunk_size: int = field(
        default=8192,
        metadata={"help": "Maximum chunk size."},
    )
    min_chunk_size: int = field(
        default=32,
        metadata={"help": "Minimum chunk size."},
    )
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for LRS."},
    )
    deadline_multiplier: float = field(
        default=1.5,
        metadata={"help": "Deadline multiplier for LRS."},
    )
    min_deadline: float = field(
        default=0.5,
        metadata={"help": "Minimum deadline for LRS."},
    )

    def get_max_num_batched_tokens(self):
        return self.max_chunk_size

    @staticmethod
    def get_type():
        return SchedulerType.LRS

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(
            self,
            "native_handle",
            LrsReplicaSchedulerConfig_C(
                self.max_batch_size,
                self.max_chunk_size,
                self.min_chunk_size,
                self.target_batch_time,
                self.deadline_multiplier,
                self.min_deadline,
            ),
        )


@dataclass(frozen=True)
class StReplicaSchedulerConfig(BaseReplicaSchedulerConfig):
    max_chunk_size: int = field(
        default=8192,
        metadata={"help": "Maximum chunk size."},
    )
    min_chunk_size: int = field(
        default=32,
        metadata={"help": "Minimum chunk size."},
    )
    target_batch_time: float = field(
        default=0.05,
        metadata={"help": "Target batch time for ST."},
    )
    deadline_multiplier: float = field(
        default=1.5,
        metadata={"help": "Deadline multiplier for ST."},
    )
    min_deadline: float = field(
        default=0.5,
        metadata={"help": "Minimum deadline for ST."},
    )
    long_seq_kv_cache_len_threshold: float = field(
        default=256 * 1024,
        metadata={
            "help": "Minimum KV cache length to be categorized as a long request."
        },
    )

    def get_max_num_batched_tokens(self):
        return self.max_chunk_size

    @staticmethod
    def get_type():
        return SchedulerType.ST

    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(
            self,
            "native_handle",
            StReplicaSchedulerConfig_C(
                self.max_batch_size,
                self.max_chunk_size,
                self.min_chunk_size,
                self.target_batch_time,
                self.deadline_multiplier,
                self.min_deadline,
                self.long_seq_kv_cache_len_threshold,
            ),
        )


@dataclass
class MetricsConfig:
    """Metric configuration."""

    write_metrics: bool = field(
        default=False, metadata={"help": "Whether to write metrics."}
    )
    wandb_project: Optional[str] = field(
        default=None, metadata={"help": "Weights & Biases project name."}
    )
    wandb_group: Optional[str] = field(
        default=None, metadata={"help": "Weights & Biases group name."}
    )
    wandb_run_name: Optional[str] = field(
        default=None, metadata={"help": "Weights & Biases run name."}
    )
    wandb_sweep_id: Optional[str] = field(
        default=None, metadata={"help": "Weights & Biases sweep ID."}
    )
    wandb_run_id: Optional[str] = field(
        default=None, metadata={"help": "Weights & Biases run ID."}
    )
    enable_gpu_op_level_metrics: bool = field(
        default=False, metadata={"help": "Enable operation-level metrics."}
    )
    enable_cpu_op_level_metrics: bool = field(
        default=False, metadata={"help": "Enable CPU operation-level metrics."}
    )
    enable_chrome_trace: bool = field(
        default=False, metadata={"help": "Enable Chrome tracing."}
    )
    keep_individual_batch_metrics: bool = field(
        default=False, metadata={"help": "Keep individual batch metrics."}
    )
    store_png: bool = field(default=False, metadata={"help": "Store PNG plots."})

    def __post_init__(self):
        self.native_handle = MetricsConfig_C(
            self.write_metrics,
            self.wandb_project,
            self.wandb_group,
            self.wandb_run_name,
            self.wandb_sweep_id,
            self.wandb_run_id,
            self.enable_gpu_op_level_metrics,
            self.enable_cpu_op_level_metrics,
            self.enable_chrome_trace,
            self.keep_individual_batch_metrics,
            self.store_png,
        )


@dataclass(frozen=True)
class WorkerConfig:
    gpu_memory_utilization: float = field(
        default=0.8, metadata={"help": "GPU memory utilization fraction (0.0 to 1.0)."}
    )
    use_native_execution_backend: bool = field(
        default=False,
        metadata={"help": "Use native execution backend for the replica."},
    )

    def __post_init__(self):
        # To circumvent frozen instance qualifier
        object.__setattr__(
            self,
            "native_handle",
            WorkerConfig_C(
                self.gpu_memory_utilization, self.use_native_execution_backend
            ),
        )
        self._verify_args()

    def _verify_args(self) -> None:
        if self.gpu_memory_utilization > 1.0:
            raise ValueError(
                "GPU memory utilization must be less than 1.0. Got "
                f"{self.gpu_memory_utilization}."
            )


@dataclass(frozen=True)
class BaseReplicaControllerConfig(BasePolyConfig):
    """Base configuration for an LLM replica controller."""

    model_config: ModelConfig = field(default_factory=ModelConfig)
    worker_config: WorkerConfig = field(default_factory=WorkerConfig)
    cache_config: CacheConfig = field(default_factory=CacheConfig)
    parallel_config: ParallelConfig = field(default_factory=ParallelConfig)
    scheduler_config: BaseReplicaSchedulerConfig = field(
        default_factory=StReplicaSchedulerConfig
    )
    metrics_config: MetricsConfig = field(default_factory=MetricsConfig)

    def __post_init__(self):
        object.__setattr__(
            self,
            "native_handle",
            BaseReplicaControllerConfig_C(
                self.model_config.native_handle,
                self.worker_config.native_handle,  # pyright: ignore
                self.cache_config.native_handle,
                self.parallel_config.native_handle,
                self.scheduler_config.native_handle,
                self.metrics_config.native_handle,
            ),
        )


@dataclass(frozen=True)
class LlmReplicaControllerConfig(BaseReplicaControllerConfig):
    """Configuration for an LLM replica controller."""

    @staticmethod
    def get_type():
        return ReplicaControllerType.LLM_BASE

    def update_cache_config(self, config: CacheConfig):
        object.__setattr__(self, "cache_config", config)

    def __post_init__(self):
        object.__setattr__(
            self,
            "native_handle",
            LlmReplicaControllerConfig_C(
                self.model_config.native_handle,
                self.worker_config.native_handle,  # pyright: ignore
                self.cache_config.native_handle,
                self.parallel_config.native_handle,
                self.scheduler_config.native_handle,
                self.metrics_config.native_handle,
            ),
        )


@dataclass(frozen=True)
class BaseReplicasetControllerConfig(BasePolyConfig):
    """Base configuration for an LLM replica set controller."""

    num_replicas: int = field(default=1, metadata={"help": "Number of replicas."})
    replica_controller_config: BaseReplicaControllerConfig = field(
        default_factory=BaseReplicaControllerConfig,
        metadata={"help": "Replica configuration for the replica set"},
    )
    replicaset_scheduler_config: BaseReplicasetSchedulerConfig = field(
        default_factory=PullReplicasetSchedulerConfig
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "native_handle",
            BaseReplicasetControllerConfig_C(
                self.num_replicas,
                self.replica_controller_config.native_handle,  # pyright: ignore
                self.replicaset_scheduler_config.native_handle,  # pyright: ignore
            ),
        )


@dataclass(frozen=True)
class LlmReplicasetControllerConfig(BaseReplicasetControllerConfig):
    """Configuration for an LLM replica set controller."""

    replica_controller_config: LlmReplicaControllerConfig = field(
        default_factory=LlmReplicaControllerConfig,
        metadata={"help": "Replica configuration for the replica set"},
    )
    num_tokenizer_workers: int = field(
        default=10, metadata={"help": "Number of tokenizer workers."}
    )

    @staticmethod
    def get_type():
        return ReplicasetControllerType.LLM

    def __post_init__(self):
        object.__setattr__(
            self,
            "native_handle",
            LlmReplicasetControllerConfig_C(
                self.num_replicas,
                self.replica_controller_config.native_handle,  # pyright: ignore
                self.replicaset_scheduler_config.native_handle,  # pyright: ignore
                self.num_tokenizer_workers,
            ),
        )


@dataclass
class InferenceEngineConfig:
    """Configuration for the inference engine."""

    controller_config: BaseReplicasetControllerConfig = field(
        default_factory=LlmReplicasetControllerConfig,
        metadata={"help": "Configuration for the LLM replica set controller"},
    )
    output_dir: str = field(
        default=".", metadata={"help": "Base output directory for the vajra engine run"}
    )
    replica_resource_mapping: Optional[Dict[int, List[Tuple[str, int]]]] = field(
        default_factory=lambda: None,
        metadata={
            "help": "Resource mapping for the replica set as a dictionary of replica_id to list of (node_ip, device_id) tuples"
        },
    )

    # Additional engine-specific configuration can be added here
    def __post_init__(self):
        controller_config = self.controller_config.native_handle  # pyright: ignore
        self.native_handle = InferenceEngineConfig_C(
            controller_config,
            self.output_dir,
            self.replica_resource_mapping,
        )


@dataclass
class BaseEndpointConfig(ABC):
    log_level: str = field(default="info", metadata={"help": "Logging level."})
    output_dir: str = field(default="output", metadata={"help": "Output directory."})
    inference_engine_config: InferenceEngineConfig = field(
        default_factory=InferenceEngineConfig
    )

    def __post_init__(self):
        self.output_dir = (
            f"{self.output_dir}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')}"
        )
        self.inference_engine_config.output_dir = self.output_dir
        self.native_handle = BaseEndpointConfig_C(
            self.inference_engine_config.native_handle,
            self.log_level,
            self.output_dir,
        )

    @classmethod
    def create_from_cli_args(cls):
        flat_config = create_flat_dataclass(cls).create_from_cli_args()
        instance = flat_config.reconstruct_original_dataclass()
        instance.__flat_config__ = flat_config
        return instance

    def to_dict(self):
        if not hasattr(self, "__flat_config__"):
            logger.warning("Flat config not found. Returning the original config.")
            return self.__dict__

        return self.__flat_config__.__dict__  # type: ignore
