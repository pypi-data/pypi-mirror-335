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
#include "native/model_executor/parallel_utils/ParallelOps.h"
//==============================================================================
using vajra::ParallelOps;
//==============================================================================
std::vector<torch::Tensor> ParallelOps::SplitTensorAlongLastDim(
    const torch::Tensor& input /*[in]*/, int64_t num_partitions /*[in]*/,
    bool contiguous_split_chunks /*[in]*/
) {
  int last_dim = input.dim() - 1;
  int last_dim_size = input.size(last_dim) / num_partitions;
  // Split
  auto tensor_list = torch::split(input, last_dim_size, last_dim);
  // Note: torch.split does not create contiguous tensors by default.
  if (contiguous_split_chunks) {
    for (auto& tensor : tensor_list) {
      tensor = tensor.contiguous();
    }
  }
  return tensor_list;
}
//==============================================================================
torch::Tensor ParallelOps::ReduceFromCacheModelParallelRegion(
    torch::Tensor& input /*[inout]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return input;
  }

  std::vector<at::Tensor> input_vec{input};

  auto work = process_group->allreduce(input_vec, c10d::AllreduceOptions());
  work->wait();
  return input;
}
//==============================================================================
torch::Tensor ParallelOps::ReduceFromTensorModelParallelRegion(
    torch::Tensor& input /*[inout]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return input;
  }

  std::vector<at::Tensor> input_vec{input};

  auto work = process_group->allreduce(input_vec, c10d::AllreduceOptions());
  work->wait();
  return input;
}
//==============================================================================
torch::Tensor ParallelOps::ScatterToTensorModelParallelRegion(
    const torch::Tensor& input /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int rank = process_group->getRank();
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return input;
  }
  std::vector<at::Tensor> input_list =
      SplitTensorAlongLastDim(input, world_size, false);
  return input_list[rank].contiguous();
}
//==============================================================================
torch::Tensor ParallelOps::GatherFromGroup(
    const torch::Tensor& input /*[in]*/, int index_rank /*[in]*/,
    int concat_dim /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();

  std::vector<at::Tensor> tensor_list(world_size, torch::empty_like(input));
  tensor_list[index_rank] = input;

  std::vector<std::vector<at::Tensor>> tensor_list_vec{tensor_list};
  std::vector<at::Tensor> input_vec{input};

  auto work = process_group->allgather(tensor_list_vec, input_vec);
  work->wait();
  return torch::cat(tensor_list, concat_dim);
}
//==============================================================================
torch::Tensor ParallelOps::GatherFromTensorModelParallelRegion(
    const torch::Tensor& input /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return input;
  }

  std::vector<at::Tensor> output_tensors(world_size, torch::empty_like(input));

  std::vector<std::vector<at::Tensor>> output_tensors_vec{output_tensors};
  std::vector<at::Tensor> input_vec{input};

  auto work = process_group->allgather(output_tensors_vec, input_vec);
  work->wait();
  return torch::cat(output_tensors, input.dim() - 1 /*last_dim*/);
}
//==============================================================================
torch::Tensor ParallelOps::GatherFromCacheModelParallelRegion(
    const torch::Tensor& input /*[in]*/, int index_rank /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return input;
  }

  return GatherFromGroup(input, index_rank, 1 /*concat_dim*/, process_group);
}
//==============================================================================
void ParallelOps::SendToNextPipelineStage(
    const torch::Tensor& input /*[in]*/, int dst_rank /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return;
  }

  std::vector<at::Tensor> input_vec{input};

  auto work = process_group->send(input_vec, dst_rank, 0 /*tag*/);
  work->wait();
}
//==============================================================================
void ParallelOps::RecvFromLastPipelineStage(
    torch::Tensor& output, /*[out]*/
    int src_rank /*[in]*/,
    c10::intrusive_ptr<c10d::ProcessGroup> process_group /*[in]*/) {
  int world_size = process_group->getSize();
  if (world_size == 1) {
    return;
  }

  std::vector<at::Tensor> output_vec{output};
  auto work = process_group->recv(output_vec, src_rank, 0 /*tag*/);
  work->wait();
}
//==============================================================================
