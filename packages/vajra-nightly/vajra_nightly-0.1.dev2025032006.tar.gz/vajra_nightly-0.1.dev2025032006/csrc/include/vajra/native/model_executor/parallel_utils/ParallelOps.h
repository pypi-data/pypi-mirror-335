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
class ParallelOps {
 public:
  static std::vector<torch::Tensor> SplitTensorAlongLastDim(
      const torch::Tensor& input /*[in]*/, int64_t num_partitions /*[in]*/,
      bool contiguous_split_chunks = false /*[in]*/
  );

  static torch::Tensor ReduceFromCacheModelParallelRegion(
      torch::Tensor& input /*[inout]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static torch::Tensor ReduceFromTensorModelParallelRegion(
      torch::Tensor& input /*[inout]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static torch::Tensor ScatterToTensorModelParallelRegion(
      const torch::Tensor& input /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static torch::Tensor GatherFromGroup(
      const torch::Tensor& input /*[in]*/, int index_rank /*[in]*/,
      int concat_dim /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static torch::Tensor GatherFromTensorModelParallelRegion(
      const torch::Tensor& input /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static torch::Tensor GatherFromCacheModelParallelRegion(
      const torch::Tensor& input /*[in]*/, int index_rank /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static void SendToNextPipelineStage(
      const torch::Tensor& input /*[in]*/, int dst_rank /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );

  static void RecvFromLastPipelineStage(
      torch::Tensor& output /*[out]*/, int src_rank /*[in]*/,
      c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/
  );
};
//==============================================================================
}  // namespace vajra
//==============================================================================
