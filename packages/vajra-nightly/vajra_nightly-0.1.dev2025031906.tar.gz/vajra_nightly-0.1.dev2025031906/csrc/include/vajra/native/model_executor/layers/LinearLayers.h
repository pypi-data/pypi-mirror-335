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

#include "commons/Logging.h"
#include "commons/StdCommon.h"
#include "native/model_executor/parallel_utils/ParallelOps.h"
#include "native/model_executor/parallel_utils/ProcessGroupWrapper.h"
//==============================================================================
namespace vajra {
//==============================================================================
class ColumnParallelLinear {
 public:
  ColumnParallelLinear(int input_size /*[in]*/, int output_size /*[in]*/,
                       bool gather_output /*[in]*/, int world_size /*[in]*/,
                       bool skip_bias_add /*[in]*/,
                       const torch::Tensor& weight /*[in]*/,
                       const std::optional<torch::Tensor>& bias /*[in]*/,
                       const std::shared_ptr<ProcessGroupWrapper>
                           process_group_wrapper /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& input /*[in]*/) const;

 private:
  int input_size_;
  int output_size_;
  bool gather_output_;
  int world_size_;
  int output_size_per_partition_;
  bool skip_bias_add_;
  const torch::Tensor weight_;
  const std::optional<torch::Tensor> bias_;
  const c10::intrusive_ptr<c10d::ProcessGroup> process_group_;
};
//==============================================================================
class RowParallelLinear {
 public:
  RowParallelLinear(int input_size /*[in]*/, int output_size /*[in]*/,
                    bool input_is_parallel /*[in]*/,
                    bool reduce_results /*[in]*/, int world_size /*[in]*/,
                    int input_size_per_partition /*[in]*/,
                    bool skip_bias_add /*[in]*/,
                    const torch::Tensor& weight /*[in]*/,
                    const std::optional<torch::Tensor>& bias /*[in]*/,
                    const std::shared_ptr<ProcessGroupWrapper>
                        process_group_wrapper /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& input /*[in]*/) const;

 private:
  int input_size_;
  int output_size_;
  bool input_is_parallel_;
  bool reduce_results_;
  int world_size_;
  int input_size_per_partition_;
  bool skip_bias_add_;
  const torch::Tensor weight_;
  const std::optional<torch::Tensor> bias_;
  const c10::intrusive_ptr<c10d::ProcessGroup> process_group_;
};
//==============================================================================
class VocabParallelEmbedding {
 public:
  VocabParallelEmbedding(int num_embeddings /*[in]*/,
                         int embedding_dim /*[in]*/,
                         int tensor_model_parallel_size /*[in]*/,
                         int rank /*[in]*/, bool reduce_results /*[in]*/,
                         int vocab_start_index /*[in]*/,
                         int vocab_end_index /*[in]*/,
                         int num_embeddings_per_partition /*[in]*/,
                         const torch::Tensor& weight /*[in]*/,
                         const std::shared_ptr<ProcessGroupWrapper>
                             process_group_wrapper /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& input /*[in]*/) const;

 private:
  int num_embeddings_;
  int embedding_dim_;
  int tensor_model_parallel_size_;
  int rank_;
  bool reduce_results_;
  int vocab_start_index_;
  int vocab_end_index_;
  int num_embeddings_per_partition_;
  const torch::Tensor weight_;
  const c10::intrusive_ptr<c10d::ProcessGroup> process_group_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
