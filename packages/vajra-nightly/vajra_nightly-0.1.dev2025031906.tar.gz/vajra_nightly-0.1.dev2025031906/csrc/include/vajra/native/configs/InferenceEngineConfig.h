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
#include "ReplicaControllerConfig.h"
#include "SchedulerConfig.h"
#include "WorkerConfig.h"
#include "commons/StdCommon.h"
//==============================================================================
namespace vajra {
//==============================================================================

struct InferenceEngineConfig final {
  InferenceEngineConfig(
      const vajra::BaseReplicasetControllerConfig controller_config,
      const std::string& output_dir = ".",
      const std::optional<
          std::map<int, std::vector<std::tuple<std::string, int>>>>&
          replica_resource_mapping = std::nullopt)
      : controller_config_(std::move(controller_config)),
        output_dir_(output_dir),
        replica_resource_mapping_(replica_resource_mapping) {}

  void set_output_dir(const std::string& output_dir) {
    output_dir_ = output_dir;
  }

  BaseReplicasetControllerConfig get_controller_config() const {
    return controller_config_;
  }

  vajra::BaseReplicasetControllerConfig controller_config_;
  std::string output_dir_;
  std::optional<std::map<int, std::vector<std::tuple<std::string, int>>>>
      replica_resource_mapping_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
