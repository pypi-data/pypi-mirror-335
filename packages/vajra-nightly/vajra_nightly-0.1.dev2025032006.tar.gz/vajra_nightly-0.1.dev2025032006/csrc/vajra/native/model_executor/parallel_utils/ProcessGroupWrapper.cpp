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
#include "native/model_executor/parallel_utils/ProcessGroupWrapper.h"
//==============================================================================
using vajra::ProcessGroupWrapper;
//==============================================================================
ProcessGroupWrapper::ProcessGroupWrapper(
    c10::intrusive_ptr<c10d::ProcessGroup> tensor_model_parallel_group /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup>
        pipeline_model_parallel_group /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> kv_parallel_group /*[in]*/)
    : tensor_model_parallel_group_(tensor_model_parallel_group),
      pipeline_model_parallel_group_(pipeline_model_parallel_group),
      kv_parallel_group_(kv_parallel_group) {}
//==============================================================================
c10::intrusive_ptr<c10d::ProcessGroup>
ProcessGroupWrapper::GetTensorModelParallelGroup() const {
  return tensor_model_parallel_group_;
}
//==============================================================================
c10::intrusive_ptr<c10d::ProcessGroup>
ProcessGroupWrapper::GetPipelineModelParallelGroup() const {
  return pipeline_model_parallel_group_;
}
//==============================================================================
c10::intrusive_ptr<c10d::ProcessGroup> ProcessGroupWrapper::GetKvParallelGroup()
    const {
  return kv_parallel_group_;
}
//==============================================================================
