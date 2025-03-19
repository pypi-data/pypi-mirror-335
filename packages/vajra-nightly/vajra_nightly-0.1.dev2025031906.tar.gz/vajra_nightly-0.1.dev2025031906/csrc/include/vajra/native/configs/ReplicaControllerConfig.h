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
#pragma once

#include "CacheConfig.h"
#include "MetricsConfig.h"
#include "ModelConfig.h"
#include "ParallelConfig.h"
#include "SchedulerConfig.h"
#include "WorkerConfig.h"
#include "commons/StdCommon.h"
//==============================================================================
namespace vajra {
//==============================================================================
enum class ReplicaControllerType { LLM_BASE, BASE };
enum class ReplicasetControllerType { LLM, BASE };

struct BaseReplicaControllerConfig {
  BaseReplicaControllerConfig(
      vajra::ModelConfig model_config_param,
      vajra::WorkerConfig worker_config_param,
      vajra::CacheConfig cache_config_param,
      vajra::ParallelConfig parallel_config_param,
      vajra::BaseReplicaSchedulerConfig scheduler_config_param,
      vajra::MetricsConfig metrics_config_param)
      : model_config(model_config_param),
        worker_config(worker_config_param),
        cache_config(cache_config_param),
        parallel_config(parallel_config_param),
        scheduler_config(scheduler_config_param),
        metrics_config(metrics_config_param) {}

  const vajra::ModelConfig model_config;
  const vajra::WorkerConfig worker_config;
  const vajra::CacheConfig cache_config;
  const vajra::ParallelConfig parallel_config;
  const vajra::BaseReplicaSchedulerConfig scheduler_config;
  const vajra::MetricsConfig metrics_config;

  static ReplicaControllerType get_type() {
    return ReplicaControllerType::BASE;
  }
};

struct LlmReplicaControllerConfig final : public BaseReplicaControllerConfig {
  LlmReplicaControllerConfig(
      vajra::ModelConfig model_config_param,
      vajra::WorkerConfig worker_config_param,
      vajra::CacheConfig cache_config_param,
      vajra::ParallelConfig parallel_config_param,
      vajra::BaseReplicaSchedulerConfig scheduler_config_param,
      vajra::MetricsConfig metrics_config_param)
      : BaseReplicaControllerConfig(model_config_param, worker_config_param,
                                    cache_config_param, parallel_config_param,
                                    scheduler_config_param,
                                    metrics_config_param) {}

  static ReplicaControllerType get_type() {
    return ReplicaControllerType::LLM_BASE;
  }
};

struct BaseReplicasetControllerConfig {
  BaseReplicasetControllerConfig(
      int num_replicas_param,
      BaseReplicaControllerConfig replica_controller_config_param,
      BaseReplicasetSchedulerConfig replicaset_scheduler_config_param)
      : num_replicas(num_replicas_param),
        replica_controller_config(replica_controller_config_param),
        replicaset_scheduler_config(replicaset_scheduler_config_param) {}

  int num_replicas;
  BaseReplicaControllerConfig replica_controller_config;
  BaseReplicasetSchedulerConfig replicaset_scheduler_config;
};

struct LlmReplicasetControllerConfig final
    : public BaseReplicasetControllerConfig {
  LlmReplicasetControllerConfig(
      int num_replicas_param,
      LlmReplicaControllerConfig replica_controller_config_param,
      BaseReplicasetSchedulerConfig replicaset_scheduler_config_param,
      int num_tokenizer_workers_param)
      : BaseReplicasetControllerConfig(num_replicas_param,
                                       replica_controller_config_param,
                                       replicaset_scheduler_config_param),
        num_tokenizer_workers(num_tokenizer_workers_param) {}

  static ReplicasetControllerType get_type() {
    return ReplicasetControllerType::LLM;
  }

  int num_tokenizer_workers;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
