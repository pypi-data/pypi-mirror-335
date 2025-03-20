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

#include "commons/StdCommon.h"
//==============================================================================
namespace vajra {
//==============================================================================
struct ModelConfig final {
  ModelConfig(std::string model_param, bool trust_remote_code_param,
              std::optional<std::string> download_dir_param,
              std::string load_format_param, std::string dtype_param,
              std::size_t seed_param, std::optional<std::string> revision_param,
              std::size_t max_model_len_param, std::size_t num_layers_param)
      : model(model_param),
        trust_remote_code(trust_remote_code_param),
        download_dir(download_dir_param),
        load_format(load_format_param),
        dtype(dtype_param),
        seed(seed_param),
        revision(revision_param),
        max_model_len(max_model_len_param),
        total_num_layers(num_layers_param) {}

  const std::string model;
  const bool trust_remote_code;
  const std::optional<std::string> download_dir;
  const std::string load_format;
  const std::string dtype;
  const std::size_t seed;
  const std::optional<std::string> revision;
  const std::size_t max_model_len;
  const std::size_t total_num_layers;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
