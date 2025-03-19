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

#include <torch/all.h>

#include <torch/csrc/distributed/c10d/ProcessGroup.hpp>

#include "commons/Logging.h"
#include "commons/StdCommon.h"
//==============================================================================
namespace vajra {
//==============================================================================
class ProcessGroupWrapper {
 public:
  ProcessGroupWrapper(
      c10::intrusive_ptr<c10d::ProcessGroup>
          tensor_model_parallel_group /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup>
          pipeline_model_parallel_group /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> kv_parallel_group /*[in]*/);

  c10::intrusive_ptr<c10d::ProcessGroup> GetTensorModelParallelGroup() const;
  c10::intrusive_ptr<c10d::ProcessGroup> GetPipelineModelParallelGroup() const;
  c10::intrusive_ptr<c10d::ProcessGroup> GetKvParallelGroup() const;

 private:
  c10::intrusive_ptr<c10d::ProcessGroup> tensor_model_parallel_group_;
  c10::intrusive_ptr<c10d::ProcessGroup> pipeline_model_parallel_group_;
  c10::intrusive_ptr<c10d::ProcessGroup> kv_parallel_group_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
