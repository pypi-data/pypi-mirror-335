//==============================================================================
// Copyright 2025 Vajra Team; Georgia Institute of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//==============================================================================
#include "native/configs/ConfigsPybind.h"

#include "commons/Logging.h"
#include "native/configs/BaseEndpointConfig.h"
#include "native/configs/CacheConfig.h"
#include "native/configs/InferenceEngineConfig.h"
#include "native/configs/MetricsConfig.h"
#include "native/configs/ModelConfig.h"
#include "native/configs/ParallelConfig.h"
#include "native/configs/ReplicaControllerConfig.h"
#include "native/configs/ReplicaResourceMapping.h"
#include "native/configs/SchedulerConfig.h"
#include "native/configs/TransferEngineConfig.h"
#include "native/configs/WorkerConfig.h"

//==============================================================================
void InitConfigsPybindSubmodule(py::module_& pm) {
  auto m = pm.def_submodule("configs", "Configs submodule");

  py::class_<vajra::ModelConfig>(m, "ModelConfig")
      .def(py::init<std::string, bool, std::optional<std::string>, std::string,
                    std::string, std::size_t, std::optional<std::string>,
                    std::size_t, std::size_t>(),
           py::arg("model"), py::arg("trust_remote_code"),
           py::arg("download_dir"), py::arg("load_format"), py::arg("dtype"),
           py::arg("seed"), py::arg("revision"), py::arg("max_model_len"),
           py::arg("total_num_layers"))
      .def_readonly("model", &vajra::ModelConfig::model)
      .def_readonly("trust_remote_code", &vajra::ModelConfig::trust_remote_code)
      .def_readonly("download_dir", &vajra::ModelConfig::download_dir)
      .def_readonly("load_format", &vajra::ModelConfig::load_format)
      .def_readonly("dtype", &vajra::ModelConfig::dtype)
      .def_readonly("seed", &vajra::ModelConfig::seed)
      .def_readonly("revision", &vajra::ModelConfig::revision)
      .def_readonly("max_model_len", &vajra::ModelConfig::max_model_len)
      .def_readonly("total_num_layers", &vajra::ModelConfig::total_num_layers)
      .def("__copy__",
           [](const vajra::ModelConfig& self) {
             return vajra::ModelConfig(self);
           })
      .def("__deepcopy__", [](const vajra::ModelConfig& self,
                              py::dict) { return vajra::ModelConfig(self); })
      .def(py::pickle(
          [](const vajra::ModelConfig& p) {
            return py::make_tuple(p.model, p.trust_remote_code, p.download_dir,
                                  p.load_format, p.dtype, p.seed, p.revision,
                                  p.max_model_len, p.total_num_layers);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(t.size() == 9,
                                 "Invalid pickled state for ModelConfig!");

            return vajra::ModelConfig(
                t[0].cast<std::string>(), t[1].cast<bool>(),
                t[2].cast<std::optional<std::string>>(),
                t[3].cast<std::string>(), t[4].cast<std::string>(),
                t[5].cast<std::size_t>(),
                t[6].cast<std::optional<std::string>>(),
                t[7].cast<std::size_t>(), t[8].cast<std::size_t>());
          }));

  //==============================================================================
  py::class_<vajra::ParallelConfig>(m, "ParallelConfig")
      .def(py::init<std::size_t, std::size_t, bool, bool, bool, std::size_t,
                    std::size_t>(),
           py::arg("pipeline_parallel_size"), py::arg("tensor_parallel_size"),
           py::arg("enable_expert_parallel"),
           py::arg("enable_sequence_pipeline_parallel"),
           py::arg("enable_chunked_pipeline_comm_opt"),
           py::arg("kv_parallel_size"), py::arg("max_num_tokens_per_kvp_group"))
      .def_readonly("pipeline_parallel_size",
                    &vajra::ParallelConfig::pipeline_parallel_size)
      .def_readonly("tensor_parallel_size",
                    &vajra::ParallelConfig::tensor_parallel_size)
      .def_readonly("enable_expert_parallel",
                    &vajra::ParallelConfig::enable_expert_parallel)
      .def_readonly("enable_sequence_pipeline_parallel",
                    &vajra::ParallelConfig::enable_sequence_pipeline_parallel)
      .def_readonly("enable_chunked_pipeline_comm_opt",
                    &vajra::ParallelConfig::enable_chunked_pipeline_comm_opt)
      .def_readonly("kv_parallel_size",
                    &vajra::ParallelConfig::kv_parallel_size)
      .def_readonly("max_num_tokens_per_kvp_group",
                    &vajra::ParallelConfig::max_num_tokens_per_kvp_group)
      .def_readonly("world_size", &vajra::ParallelConfig::world_size)
      .def("__copy__",
           [](const vajra::ParallelConfig& self) {
             return vajra::ParallelConfig(self);
           })
      .def("__deepcopy__", [](const vajra::ParallelConfig& self,
                              py::dict) { return vajra::ParallelConfig(self); })
      .def(py::pickle(
          [](const vajra::ParallelConfig& p) {
            return py::make_tuple(
                p.pipeline_parallel_size, p.tensor_parallel_size,
                p.enable_expert_parallel, p.enable_sequence_pipeline_parallel,
                p.enable_chunked_pipeline_comm_opt, p.kv_parallel_size,
                p.max_num_tokens_per_kvp_group);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(t.size() == 7,
                                 "Invalid pickled state for ParallelConfig!");

            return vajra::ParallelConfig(
                t[0].cast<std::size_t>(), t[1].cast<std::size_t>(),
                t[2].cast<bool>(), t[3].cast<bool>(), t[4].cast<bool>(),
                t[5].cast<std::size_t>(), t[6].cast<std::size_t>());
          }));

  //==============================================================================
  py::class_<vajra::ReplicaResourceConfig>(m, "ReplicaResourceConfig")
      .def(py::init<vajra::ParallelConfig&, vajra::ModelConfig&>(),
           py::arg("parallel_config"), py::arg("model_config"))
      .def("__str__", &vajra::ReplicaResourceConfig::ToString)
      .def("__repr__", &vajra::ReplicaResourceConfig::ToString)
      .def_readonly("tensor_parallel_size",
                    &vajra::ReplicaResourceConfig::tensor_parallel_size)
      .def_readonly("pipeline_parallel_size",
                    &vajra::ReplicaResourceConfig::pipeline_parallel_size)
      .def_readonly("kv_parallel_size",
                    &vajra::ReplicaResourceConfig::kv_parallel_size)
      .def_readonly("local_num_layers",
                    &vajra::ReplicaResourceConfig::local_num_layers)
      .def_readonly("total_num_layers",
                    &vajra::ReplicaResourceConfig::total_num_layers)
      .def_readonly("world_size", &vajra::ReplicaResourceConfig::world_size);

  //==============================================================================
  py::class_<vajra::TransferEngineConfig>(m, "TransferEngineConfig")
      .def(py::init<vajra::TransferBackendType, std::size_t,
                    const vajra::ReplicaResourceMapping&,
                    c10::intrusive_ptr<c10d::ProcessGroup>>(),
           py::arg("transfer_backend_type"), py::arg("global_rank"),
           py::arg("replica_mapping"), py::arg("global_process_group"))
      .def_readonly("transfer_backend_type",
                    &vajra::TransferEngineConfig::transfer_backend_type)
      .def_readonly("global_rank", &vajra::TransferEngineConfig::global_rank)
      .def_readonly("replica_mapping",
                    &vajra::TransferEngineConfig::replica_mapping)
      .def_readonly("global_process_group",
                    &vajra::TransferEngineConfig::global_process_group);

  //==============================================================================
  py::class_<vajra::CacheConfig, std::shared_ptr<vajra::CacheConfig>>(
      m, "CacheConfig")
      .def(py::init<int, int>(), py::arg("block_size"),
           py::arg("num_gpu_blocks"))
      .def_readonly("block_size", &vajra::CacheConfig::block_size)
      .def_readonly("num_gpu_blocks", &vajra::CacheConfig::num_gpu_blocks)
      .def("__copy__",
           [](const vajra::CacheConfig& self) {
             return vajra::CacheConfig(self);
           })
      .def("__deepcopy__", [](const vajra::CacheConfig& self,
                              py::dict) { return vajra::CacheConfig(self); })
      .def(py::pickle(
          [](const vajra::CacheConfig& p) {  // __getstate__
            return py::make_tuple(p.block_size, p.num_gpu_blocks);
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(t.size() == 2,
                                 "Invalid pickled state for CacheConfig!");

            return vajra::CacheConfig(t[0].cast<int>(), t[1].cast<int>());
          }));

  //==============================================================================
  py::enum_<vajra::SchedulerType>(m, "SchedulerType")
      .value("FCFS", vajra::SchedulerType::FCFS)
      .value("FCFS_FIXED_CHUNK", vajra::SchedulerType::FCFS_FIXED_CHUNK)
      .value("EDF", vajra::SchedulerType::EDF)
      .value("LRS", vajra::SchedulerType::LRS)
      .value("ST", vajra::SchedulerType::ST);

  //==============================================================================
  py::class_<vajra::BaseReplicaSchedulerConfig>(m, "BaseReplicaSchedulerConfig")
      .def(py::init<std::size_t>(), py::arg("max_batch_size") = 128)
      .def("get_max_num_batched_tokens",
           &vajra::BaseReplicaSchedulerConfig::get_max_num_batched_tokens)
      .def_readonly("max_batch_size",
                    &vajra::BaseReplicaSchedulerConfig::max_batch_size)
      .def("__copy__",
           [](const vajra::BaseReplicaSchedulerConfig& self) {
             return vajra::BaseReplicaSchedulerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::BaseReplicaSchedulerConfig& self, py::dict) {
             return vajra::BaseReplicaSchedulerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::BaseReplicaSchedulerConfig& p) {
            return py::make_tuple(p.max_batch_size);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(
                t.size() == 1,
                "Invalid pickled state for BaseReplicaSchedulerConfig!");
            return vajra::BaseReplicaSchedulerConfig(t[0].cast<std::size_t>());
          }));

  //==============================================================================
  py::class_<vajra::FcfsFixedChunkReplicaSchedulerConfig,
             vajra::BaseReplicaSchedulerConfig>(
      m, "FcfsFixedChunkReplicaSchedulerConfig")
      .def(py::init<std::size_t, std::size_t>(),
           py::arg("max_batch_size") = 128, py::arg("chunk_size") = 2048)
      .def("get_max_num_batched_tokens",
           &vajra::FcfsFixedChunkReplicaSchedulerConfig::
               get_max_num_batched_tokens)
      .def_static("get_type",
                  &vajra::FcfsFixedChunkReplicaSchedulerConfig::get_type)
      .def_readonly("chunk_size",
                    &vajra::FcfsFixedChunkReplicaSchedulerConfig::chunk_size)
      .def("__copy__",
           [](const vajra::FcfsFixedChunkReplicaSchedulerConfig& self) {
             return vajra::FcfsFixedChunkReplicaSchedulerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::FcfsFixedChunkReplicaSchedulerConfig& self,
              py::dict) {
             return vajra::FcfsFixedChunkReplicaSchedulerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::FcfsFixedChunkReplicaSchedulerConfig& self) {
            return py::make_tuple(self.max_batch_size, self.chunk_size);
          },
          [](py::tuple t) {
            if (t.size() != 2)
              throw std::runtime_error(
                  "Invalid state for FcfsFixedChunkReplicaSchedulerConfig!");

            return vajra::FcfsFixedChunkReplicaSchedulerConfig(
                t[0].cast<std::size_t>(),  // max_batch_size
                t[1].cast<std::size_t>()   // chunk_size
            );
          }));
  //==============================================================================
  py::class_<vajra::FcfsReplicaSchedulerConfig,
             vajra::BaseReplicaSchedulerConfig>(m, "FcfsReplicaSchedulerConfig")
      .def(py::init<std::size_t, std::size_t, std::size_t, float>(),
           py::arg("max_batch_size") = 128, py::arg("max_chunk_size") = 8192,
           py::arg("min_chunk_size") = 32, py::arg("target_batch_time") = 0.05)
      .def("get_max_num_batched_tokens",
           &vajra::FcfsReplicaSchedulerConfig::get_max_num_batched_tokens)
      .def_static("get_type", &vajra::FcfsReplicaSchedulerConfig::get_type)
      .def_readonly("max_chunk_size",
                    &vajra::FcfsReplicaSchedulerConfig::max_chunk_size)
      .def_readonly("min_chunk_size",
                    &vajra::FcfsReplicaSchedulerConfig::min_chunk_size)
      .def_readonly("target_batch_time",
                    &vajra::FcfsReplicaSchedulerConfig::target_batch_time)
      .def("__copy__",
           [](const vajra::FcfsReplicaSchedulerConfig& self) {
             return vajra::FcfsReplicaSchedulerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::FcfsReplicaSchedulerConfig& self, py::dict) {
             return vajra::FcfsReplicaSchedulerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::FcfsReplicaSchedulerConfig& self) {
            return py::make_tuple(self.max_chunk_size, self.min_chunk_size,
                                  self.target_batch_time);
          },
          [](py::tuple t) {
            if (t.size() != 3)
              throw std::runtime_error(
                  "Invalid state for FcfsReplicaSchedulerConfig!");

            return vajra::FcfsReplicaSchedulerConfig(t[0].cast<std::size_t>(),
                                                     t[1].cast<std::size_t>(),
                                                     t[2].cast<float>());
          }));

  //==============================================================================
  py::class_<vajra::EdfReplicaSchedulerConfig,
             vajra::BaseReplicaSchedulerConfig>(m, "EdfReplicaSchedulerConfig")
      .def(py::init<std::size_t, std::size_t, std::size_t, float, float,
                    float>(),
           py::arg("max_batch_size") = 128, py::arg("max_chunk_size") = 8192,
           py::arg("min_chunk_size") = 32, py::arg("target_batch_time") = 0.05,
           py::arg("deadline_multiplier") = 1.5, py::arg("min_deadline") = 0.5)
      .def("get_max_num_batched_tokens",
           &vajra::EdfReplicaSchedulerConfig::get_max_num_batched_tokens)
      .def_static("get_type", &vajra::EdfReplicaSchedulerConfig::get_type)
      .def_readonly("max_chunk_size",
                    &vajra::EdfReplicaSchedulerConfig::max_chunk_size)
      .def_readonly("min_chunk_size",
                    &vajra::EdfReplicaSchedulerConfig::min_chunk_size)
      .def_readonly("target_batch_time",
                    &vajra::EdfReplicaSchedulerConfig::target_batch_time)
      .def_readonly("deadline_multiplier",
                    &vajra::EdfReplicaSchedulerConfig::deadline_multiplier)
      .def_readonly("min_deadline",
                    &vajra::EdfReplicaSchedulerConfig::min_deadline)
      .def("__copy__",
           [](const vajra::EdfReplicaSchedulerConfig& self) {
             return vajra::EdfReplicaSchedulerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::EdfReplicaSchedulerConfig& self, py::dict) {
             return vajra::EdfReplicaSchedulerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::EdfReplicaSchedulerConfig& self) {
            return py::make_tuple(self.max_chunk_size, self.min_chunk_size,
                                  self.target_batch_time,
                                  self.deadline_multiplier, self.min_deadline);
          },
          [](py::tuple t) {
            if (t.size() != 5)
              throw std::runtime_error(
                  "Invalid state for EdfReplicaSchedulerConfig!");

            return vajra::EdfReplicaSchedulerConfig(
                t[0].cast<std::size_t>(), t[1].cast<std::size_t>(),
                t[2].cast<float>(), t[3].cast<float>(), t[4].cast<float>());
          }));

  //==============================================================================
  py::class_<vajra::LrsReplicaSchedulerConfig,
             vajra::BaseReplicaSchedulerConfig>(m, "LrsReplicaSchedulerConfig")
      .def(py::init<std::size_t, std::size_t, std::size_t, float, float,
                    float>(),
           py::arg("max_batch_size") = 128, py::arg("max_chunk_size") = 8192,
           py::arg("min_chunk_size") = 32, py::arg("target_batch_time") = 0.05,
           py::arg("deadline_multiplier") = 1.5, py::arg("min_deadline") = 0.5)
      .def("get_max_num_batched_tokens",
           &vajra::LrsReplicaSchedulerConfig::get_max_num_batched_tokens)
      .def_static("get_type", &vajra::LrsReplicaSchedulerConfig::get_type)
      .def_readonly("max_chunk_size",
                    &vajra::LrsReplicaSchedulerConfig::max_chunk_size)
      .def_readonly("min_chunk_size",
                    &vajra::LrsReplicaSchedulerConfig::min_chunk_size)
      .def_readonly("target_batch_time",
                    &vajra::LrsReplicaSchedulerConfig::target_batch_time)
      .def_readonly("deadline_multiplier",
                    &vajra::LrsReplicaSchedulerConfig::deadline_multiplier)
      .def_readonly("min_deadline",
                    &vajra::LrsReplicaSchedulerConfig::min_deadline)
      .def("__copy__",
           [](const vajra::LrsReplicaSchedulerConfig& self) {
             return vajra::LrsReplicaSchedulerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::LrsReplicaSchedulerConfig& self, py::dict) {
             return vajra::LrsReplicaSchedulerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::LrsReplicaSchedulerConfig& self) {
            return py::make_tuple(self.max_chunk_size, self.min_chunk_size,
                                  self.target_batch_time,
                                  self.deadline_multiplier, self.min_deadline);
          },
          [](py::tuple t) {
            if (t.size() != 5)
              throw std::runtime_error(
                  "Invalid state for LrsReplicaSchedulerConfig!");

            return vajra::LrsReplicaSchedulerConfig(
                t[0].cast<std::size_t>(), t[1].cast<std::size_t>(),
                t[2].cast<float>(), t[3].cast<float>(), t[4].cast<float>());
          }));

  //==============================================================================
  py::class_<vajra::StReplicaSchedulerConfig,
             vajra::BaseReplicaSchedulerConfig>(m, "StReplicaSchedulerConfig")
      .def(py::init<std::size_t, std::size_t, std::size_t, float, float, float,
                    std::size_t>(),
           py::arg("max_batch_size") = 128, py::arg("max_chunk_size") = 8192,
           py::arg("min_chunk_size") = 32, py::arg("target_batch_time") = 0.05,
           py::arg("deadline_multiplier") = 1.5, py::arg("min_deadline") = 0.5,
           py::arg("long_seq_kv_cache_len_threshold") = 256 * 1024)
      .def("get_max_num_batched_tokens",
           &vajra::StReplicaSchedulerConfig::get_max_num_batched_tokens)
      .def_static("get_type", &vajra::StReplicaSchedulerConfig::get_type)
      .def_readonly("max_chunk_size",
                    &vajra::StReplicaSchedulerConfig::max_chunk_size)
      .def_readonly("min_chunk_size",
                    &vajra::StReplicaSchedulerConfig::min_chunk_size)
      .def_readonly("target_batch_time",
                    &vajra::StReplicaSchedulerConfig::target_batch_time)
      .def_readonly("deadline_multiplier",
                    &vajra::StReplicaSchedulerConfig::deadline_multiplier)
      .def_readonly("min_deadline",
                    &vajra::StReplicaSchedulerConfig::min_deadline)
      .def_readonly(
          "long_seq_kv_cache_len_threshold",
          &vajra::StReplicaSchedulerConfig::long_seq_kv_cache_len_threshold)
      .def("__copy__",
           [](const vajra::StReplicaSchedulerConfig& self) {
             return vajra::StReplicaSchedulerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::StReplicaSchedulerConfig& self, py::dict) {
             return vajra::StReplicaSchedulerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::StReplicaSchedulerConfig& self) {
            return py::make_tuple(self.max_batch_size, self.max_chunk_size,
                                  self.min_chunk_size, self.target_batch_time,
                                  self.deadline_multiplier, self.min_deadline,
                                  self.long_seq_kv_cache_len_threshold);
          },
          [](py::tuple t) {
            if (t.size() != 7)
              throw std::runtime_error(
                  "Invalid state for StReplicaSchedulerConfig!");

            return vajra::StReplicaSchedulerConfig(
                t[0].cast<std::size_t>(), t[1].cast<std::size_t>(),
                t[2].cast<std::size_t>(), t[3].cast<float>(),
                t[4].cast<float>(), t[5].cast<float>(),
                t[6].cast<std::size_t>());
          }));

  //==============================================================================
  py::class_<vajra::MetricsConfig>(m, "MetricsConfig")
      .def(
          py::init<bool, std::optional<std::string>, std::optional<std::string>,
                   std::optional<std::string>, std::optional<std::string>,
                   std::optional<std::string>, bool, bool, bool, bool, bool>())
      .def_readonly("write_metrics", &vajra::MetricsConfig::write_metrics)
      .def_readonly("wandb_project", &vajra::MetricsConfig::wandb_project)
      .def_readonly("wandb_group", &vajra::MetricsConfig::wandb_group)
      .def_readonly("wandb_run_name", &vajra::MetricsConfig::wandb_run_name)
      .def_readonly("wandb_sweep_id", &vajra::MetricsConfig::wandb_sweep_id)
      .def_readonly("wandb_run_id", &vajra::MetricsConfig::wandb_run_id)
      .def_readonly("enable_gpu_op_level_metrics",
                    &vajra::MetricsConfig::enable_gpu_op_level_metrics)
      .def_readonly("enable_cpu_op_level_metrics",
                    &vajra::MetricsConfig::enable_cpu_op_level_metrics)
      .def_readonly("enable_chrome_trace",
                    &vajra::MetricsConfig::enable_chrome_trace)
      .def_readonly("keep_individual_batch_metrics",
                    &vajra::MetricsConfig::keep_individual_batch_metrics)
      .def_readonly("store_png", &vajra::MetricsConfig::store_png)
      .def("__copy__",
           [](const vajra::MetricsConfig& self) {
             return vajra::MetricsConfig(self);
           })
      .def("__deepcopy__", [](const vajra::MetricsConfig& self,
                              py::dict) { return vajra::MetricsConfig(self); })
      .def(py::pickle(
          [](const vajra::MetricsConfig& p) {
            return py::make_tuple(p.write_metrics, p.wandb_project,
                                  p.wandb_group, p.wandb_run_name,
                                  p.wandb_sweep_id, p.wandb_run_id);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(t.size() == 6,
                                 "Invalid pickled state for MetricsConfig!");
            return vajra::MetricsConfig(t[0].cast<bool>(),
                                        t[1].cast<std::optional<std::string>>(),
                                        t[2].cast<std::optional<std::string>>(),
                                        t[3].cast<std::optional<std::string>>(),
                                        t[4].cast<std::optional<std::string>>(),
                                        t[5].cast<std::optional<std::string>>(),
                                        false, false, false, false, false);
          }));

  //==============================================================================
  py::class_<vajra::WorkerConfig>(m, "WorkerConfig")
      .def(py::init<float, bool>())
      .def_readonly("gpu_memory_utilization",
                    &vajra::WorkerConfig::gpu_memory_utilization)
      .def_readonly("use_native_execution_backend",
                    &vajra::WorkerConfig::use_native_execution_backend)
      .def("__copy__",
           [](const vajra::WorkerConfig& self) {
             return vajra::WorkerConfig(self);
           })
      .def("__deepcopy__", [](const vajra::WorkerConfig& self,
                              py::dict) { return vajra::WorkerConfig(self); })
      .def(py::pickle(
          [](const vajra::WorkerConfig& self) {
            return py::make_tuple(self.gpu_memory_utilization,
                                  self.use_native_execution_backend);
          },
          [](py::tuple t) {
            if (t.size() != 2)
              throw std::runtime_error(
                  "Invalid pickled state for WorkerConfig");

            return vajra::WorkerConfig(t[0].cast<float>(), t[1].cast<bool>());
          }));

  //==============================================================================
  py::enum_<vajra::ReplicasetSchedulerType>(m, "ReplicasetSchedulerType")
      .value("PULL", vajra::ReplicasetSchedulerType::PULL)
      .value("ROUND_ROBIN", vajra::ReplicasetSchedulerType::ROUND_ROBIN)
      .export_values();

  py::enum_<vajra::ReplicaControllerType>(m, "ReplicaControllerType")
      .value("LLM_BASE", vajra::ReplicaControllerType::LLM_BASE)
      .export_values();

  py::enum_<vajra::ReplicasetControllerType>(m, "ReplicasetControllerType")
      .value("LLM", vajra::ReplicasetControllerType::LLM)
      .export_values();

  // ==============================================================================
  py::class_<vajra::BaseReplicasetSchedulerConfig>(
      m, "BaseReplicasetSchedulerConfig")
      .def(
          "__copy__",
          [](const vajra::BaseReplicasetSchedulerConfig& self) {
            return std::make_unique<vajra::BaseReplicasetSchedulerConfig>(self);
          })
      .def(
          "__deepcopy__",
          [](const vajra::BaseReplicasetSchedulerConfig& self, py::dict) {
            return std::make_unique<vajra::BaseReplicasetSchedulerConfig>(self);
          })
      .def(py::pickle(
          [](const vajra::BaseReplicasetSchedulerConfig& self) {
            return py::make_tuple();
          },
          [](py::tuple t) {
            if (t.size() != 0) throw std::runtime_error("Invalid state!");
            return std::make_unique<vajra::BaseReplicasetSchedulerConfig>();
          }));

  //==============================================================================
  py::class_<vajra::PullReplicasetSchedulerConfig,
             vajra::BaseReplicasetSchedulerConfig>(
      m, "PullReplicasetSchedulerConfig")
      .def(py::init<>())
      .def_static("get_type", &vajra::PullReplicasetSchedulerConfig::get_type)
      .def(
          "__copy__",
          [](const vajra::PullReplicasetSchedulerConfig& self) {
            return std::make_unique<vajra::PullReplicasetSchedulerConfig>(self);
          })
      .def(
          "__deepcopy__",
          [](const vajra::PullReplicasetSchedulerConfig& self, py::dict) {
            return std::make_unique<vajra::PullReplicasetSchedulerConfig>(self);
          })
      .def(py::pickle(
          [](const vajra::PullReplicasetSchedulerConfig& self) {
            return py::make_tuple();
          },
          [](py::tuple t) {
            if (t.size() != 0) throw std::runtime_error("Invalid state!");
            return std::make_unique<vajra::PullReplicasetSchedulerConfig>();
          }));

  //==============================================================================
  py::class_<vajra::RoundRobinReplicasetSchedulerConfig,
             vajra::BaseReplicasetSchedulerConfig>(
      m, "RoundRobinReplicasetSchedulerConfig")
      .def(py::init<>())
      .def_static("get_type",
                  &vajra::RoundRobinReplicasetSchedulerConfig::get_type)
      .def(
          "__copy__",
          [](const vajra::RoundRobinReplicasetSchedulerConfig& self) {
            return std::make_unique<vajra::RoundRobinReplicasetSchedulerConfig>(
                self);
          })
      .def(
          "__deepcopy__",
          [](const vajra::RoundRobinReplicasetSchedulerConfig& self, py::dict) {
            return std::make_unique<vajra::RoundRobinReplicasetSchedulerConfig>(
                self);
          })
      .def(py::pickle(
          [](const vajra::RoundRobinReplicasetSchedulerConfig& self) {
            return py::make_tuple();
          },
          [](py::tuple t) {
            if (t.size() != 0) throw std::runtime_error("Invalid state!");

            return std::make_unique<
                vajra::RoundRobinReplicasetSchedulerConfig>();
          }));

  //==============================================================================
  py::class_<vajra::BaseReplicaControllerConfig>(m,
                                                 "BaseReplicaControllerConfig")
      .def(py::init<vajra::ModelConfig, vajra::WorkerConfig, vajra::CacheConfig,
                    vajra::ParallelConfig, vajra::BaseReplicaSchedulerConfig,
                    vajra::MetricsConfig>(),
           py::arg("model_config"), py::arg("worker_config"),
           py::arg("cache_config"), py::arg("parallel_config"),
           py::arg("scheduler_config"), py::arg("metrics_config"))
      .def_readonly("model_config",
                    &vajra::BaseReplicaControllerConfig::model_config)
      .def_readonly("worker_config",
                    &vajra::BaseReplicaControllerConfig::worker_config)
      .def_readonly("cache_config",
                    &vajra::BaseReplicaControllerConfig::cache_config)
      .def_readonly("parallel_config",
                    &vajra::BaseReplicaControllerConfig::parallel_config)
      .def_readonly("scheduler_config",
                    &vajra::BaseReplicaControllerConfig::scheduler_config)
      .def_readonly("metrics_config",
                    &vajra::BaseReplicaControllerConfig::metrics_config)
      .def("__copy__",
           [](const vajra::BaseReplicaControllerConfig& self) {
             return vajra::BaseReplicaControllerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::BaseReplicaControllerConfig& self, py::dict) {
             return vajra::BaseReplicaControllerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::BaseReplicaControllerConfig& self) {
            return py::make_tuple(self.model_config, self.worker_config,
                                  self.cache_config, self.parallel_config,
                                  self.scheduler_config, self.metrics_config);
          },
          [](py::tuple t) {
            if (t.size() != 6)
              throw std::runtime_error(
                  "Invalid pickled state for BaseReplicaControllerConfig");

            return vajra::BaseReplicaControllerConfig(
                t[0].cast<vajra::ModelConfig>(),
                t[1].cast<vajra::WorkerConfig>(),
                t[2].cast<vajra::CacheConfig>(),
                t[3].cast<vajra::ParallelConfig>(),
                t[4].cast<vajra::BaseReplicaSchedulerConfig>(),
                t[5].cast<vajra::MetricsConfig>());
          }));
  //==============================================================================
  py::class_<vajra::LlmReplicaControllerConfig,
             vajra::BaseReplicaControllerConfig>(m,
                                                 "LlmReplicaControllerConfig")
      .def(py::init<vajra::ModelConfig, vajra::WorkerConfig, vajra::CacheConfig,
                    vajra::ParallelConfig, vajra::BaseReplicaSchedulerConfig,
                    vajra::MetricsConfig>(),
           py::arg("model_config"), py::arg("worker_config"),
           py::arg("cache_config"), py::arg("parallel_config"),
           py::arg("scheduler_config"), py::arg("metrics_config"))
      .def_static("get_type", &vajra::LlmReplicaControllerConfig::get_type)
      .def("__copy__",
           [](const vajra::LlmReplicaControllerConfig& self) {
             return vajra::LlmReplicaControllerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::LlmReplicaControllerConfig& self, py::dict) {
             return vajra::LlmReplicaControllerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::LlmReplicaControllerConfig& self) -> py::tuple {
            return py::make_tuple(self.model_config, self.worker_config,
                                  self.cache_config, self.parallel_config,
                                  self.scheduler_config, self.metrics_config);
          },
          [](py::tuple t) -> vajra::LlmReplicaControllerConfig {
            if (t.size() != 6)
              throw std::runtime_error(
                  "Invalid pickled state for LlmReplicaControllerConfig");

            return vajra::LlmReplicaControllerConfig(
                t[0].cast<vajra::ModelConfig>(),
                t[1].cast<vajra::WorkerConfig>(),
                t[2].cast<vajra::CacheConfig>(),
                t[3].cast<vajra::ParallelConfig>(),
                t[4].cast<vajra::BaseReplicaSchedulerConfig>(),
                t[5].cast<vajra::MetricsConfig>());
          }));
  //==============================================================================
  py::class_<vajra::BaseReplicasetControllerConfig>(
      m, "BaseReplicasetControllerConfig")
      .def(py::init<int, vajra::BaseReplicaControllerConfig,
                    vajra::BaseReplicasetSchedulerConfig>(),
           py::arg("num_replicas"), py::arg("replica_controller_config"),
           py::arg("replicaset_scheduler_config"))
      .def_readonly("num_replicas",
                    &vajra::BaseReplicasetControllerConfig::num_replicas)
      .def_readonly(
          "replica_controller_config",
          &vajra::BaseReplicasetControllerConfig::replica_controller_config)
      .def_readonly(
          "replicaset_scheduler_config",
          &vajra::BaseReplicasetControllerConfig::replicaset_scheduler_config)
      .def("__copy__",
           [](const vajra::BaseReplicasetControllerConfig& self) {
             return vajra::BaseReplicasetControllerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::BaseReplicasetControllerConfig& self, py::dict) {
             return vajra::BaseReplicasetControllerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::BaseReplicasetControllerConfig& self) {
            return py::make_tuple(self.num_replicas,
                                  self.replica_controller_config,
                                  self.replicaset_scheduler_config);
          },
          [](py::tuple t) {
            if (t.size() != 3)
              throw std::runtime_error(
                  "Invalid pickled state for BaseReplicasetControllerConfig");

            return vajra::BaseReplicasetControllerConfig(
                t[0].cast<int>(),
                t[1].cast<vajra::BaseReplicaControllerConfig>(),
                t[2].cast<vajra::BaseReplicasetSchedulerConfig>());
          }));
  //==============================================================================
  py::class_<vajra::LlmReplicasetControllerConfig,
             vajra::BaseReplicasetControllerConfig>(
      m, "LlmReplicasetControllerConfig")
      .def(py::init<int, vajra::LlmReplicaControllerConfig,
                    vajra::BaseReplicasetSchedulerConfig, int>(),
           py::arg("num_replicas"), py::arg("replica_controller_config"),
           py::arg("replicaset_scheduler_config"),
           py::arg("num_tokenizer_workers"))
      .def_static("get_type", &vajra::LlmReplicasetControllerConfig::get_type)
      .def_readonly(
          "num_tokenizer_workers",
          &vajra::LlmReplicasetControllerConfig::num_tokenizer_workers)
      .def("__copy__",
           [](const vajra::LlmReplicasetControllerConfig& self) {
             return vajra::LlmReplicasetControllerConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::LlmReplicasetControllerConfig& self, py::dict) {
             return vajra::LlmReplicasetControllerConfig(self);
           })
      .def(py::pickle(
          [](const vajra::LlmReplicasetControllerConfig& self) {
            return py::make_tuple(
                self.num_replicas, self.replica_controller_config,
                self.replicaset_scheduler_config, self.num_tokenizer_workers);
          },
          [](py::tuple t) {
            if (t.size() != 4)
              throw std::runtime_error(
                  "Invalid state for LlmReplicasetControllerConfig!");

            vajra::BaseReplicasetSchedulerConfig scheduler_config;
            if (!t[2].is_none()) {
              scheduler_config =
                  t[2].cast<vajra::BaseReplicasetSchedulerConfig>();
            }

            auto baseObj = t[1].cast<vajra::BaseReplicaControllerConfig>();

            if (baseObj.get_type() == vajra::ReplicaControllerType::BASE) {
              // Downcast the base object to LlmReplicaControllerConfig
              vajra::LlmReplicaControllerConfig llm_config =
                  static_cast<const vajra::LlmReplicaControllerConfig&>(
                      baseObj);

              return vajra::LlmReplicasetControllerConfig(
                  t[0].cast<int>(), llm_config, scheduler_config,
                  t[3].cast<int>());
            } else {
              return vajra::LlmReplicasetControllerConfig(
                  t[0].cast<int>(),
                  t[1].cast<vajra::LlmReplicaControllerConfig>(),
                  scheduler_config, t[3].cast<int>());
            }
          }));

  //==============================================================================
  py::class_<vajra::InferenceEngineConfig>(m, "InferenceEngineConfig")
      .def(
          py::init<
              const vajra::BaseReplicasetControllerConfig&, const std::string&,
              const std::optional<
                  std::map<int, std::vector<std::tuple<std::string, int>>>>&>(),
          py::arg("controller_config"), py::arg("output_dir") = ".",
          py::arg("replica_resource_mapping") = std::nullopt)
      .def_property_readonly(
          "controller_config",
          [](const vajra::InferenceEngineConfig& self)
              -> const vajra::BaseReplicasetControllerConfig& {
            return self.controller_config_;
          })
      .def_readwrite("output_dir", &vajra::InferenceEngineConfig::output_dir_)
      .def_readwrite("replica_resource_mapping",
                     &vajra::InferenceEngineConfig::replica_resource_mapping_)
      .def("set_output_dir", &vajra::InferenceEngineConfig::set_output_dir)
      .def("__copy__",
           [](const vajra::InferenceEngineConfig& self) {
             return vajra::InferenceEngineConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::InferenceEngineConfig& self, py::dict) {
             return vajra::InferenceEngineConfig(self);
           })
      .def(py::pickle(
          [](const vajra::InferenceEngineConfig& self) {
            return py::make_tuple(self.controller_config_, self.output_dir_,
                                  self.replica_resource_mapping_);
          },
          [](py::tuple t) {
            if (t.size() != 3) {
              throw std::runtime_error(
                  "Invalid pickled state for InferenceEngineConfig");
            }
            return vajra::InferenceEngineConfig(
                t[0].cast<vajra::BaseReplicasetControllerConfig>(),
                t[1].cast<std::string>(),
                t[2].cast<std::optional<std::map<
                    int, std::vector<std::tuple<std::string, int>>>>>());
          }));
  //==============================================================================
  py::class_<vajra::BaseEndpointConfig>(m, "BaseEndpointConfig")
      .def(py::init<const vajra::InferenceEngineConfig&, const std::string&,
                    const std::string&>(),
           py::arg("inference_engine_config"), py::arg("log_level") = "info",
           py::arg("output_dir") = "output")
      .def_readwrite("log_level", &vajra::BaseEndpointConfig::log_level_)
      .def_readwrite("output_dir", &vajra::BaseEndpointConfig::output_dir_)
      .def_readwrite("flat_config", &vajra::BaseEndpointConfig::flat_config_)
      .def("__copy__",
           [](const vajra::BaseEndpointConfig& self) {
             return vajra::BaseEndpointConfig(self);
           })
      .def("__deepcopy__",
           [](const vajra::BaseEndpointConfig& self, py::dict) {
             return vajra::BaseEndpointConfig(self);
           })
      .def(py::pickle(
          [](const vajra::BaseEndpointConfig& self) {
            return py::make_tuple(self.log_level_, self.output_dir_,
                                  self.inference_engine_config_,
                                  self.flat_config_);
          },
          [](py::tuple t) {
            if (t.size() != 4)
              throw std::runtime_error(
                  "Invalid pickled state for BaseEndpointConfig");

            std::string log_level = t[0].cast<std::string>();
            std::string output_dir = t[1].cast<std::string>();
            vajra::InferenceEngineConfig engine_config =
                t[2].cast<vajra::InferenceEngineConfig>();
            std::map<std::string, std::string> flat_config =
                t[3].cast<std::map<std::string, std::string>>();

            vajra::BaseEndpointConfig config(engine_config, log_level,
                                             output_dir);
            config.flat_config_ = flat_config;
            return config;
          }));
}  // NOLINT(readability/fn_size)
//==============================================================================
