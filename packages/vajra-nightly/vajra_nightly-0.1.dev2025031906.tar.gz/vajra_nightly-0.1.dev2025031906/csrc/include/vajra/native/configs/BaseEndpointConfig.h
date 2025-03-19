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

#include "InferenceEngineConfig.h"
#include "commons/StdCommon.h"
//==============================================================================
namespace vajra {
//==============================================================================
struct BaseEndpointConfig final {
  BaseEndpointConfig(
      const vajra::InferenceEngineConfig& inference_engine_config,
      const std::string& log_level = "info",
      const std::string& output_dir = "output")
      : log_level_(log_level),
        output_dir_(output_dir),
        inference_engine_config_(inference_engine_config) {}

  virtual ~BaseEndpointConfig() = default;

  std::string log_level_;
  std::string output_dir_;
  vajra::InferenceEngineConfig inference_engine_config_;
  std::map<std::string, std::string> flat_config_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
