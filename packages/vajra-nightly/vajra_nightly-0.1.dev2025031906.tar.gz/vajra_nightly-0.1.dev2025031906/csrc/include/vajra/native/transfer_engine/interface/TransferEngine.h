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

#include "commons/StdCommon.h"
#include "native/configs/ReplicaResourceMapping.h"
#include "native/transfer_engine/interface/TransferWork.h"
//==============================================================================
namespace vajra {
//==============================================================================
class TransferEngine {
 public:
  virtual ~TransferEngine() = default;

  virtual std::unique_ptr<TransferWork> AsyncSend(
      std::size_t dst_replica_id /*[in]*/,
      const torch::Tensor& page_tensor /*[in]*/,
      const std::vector<std::size_t>& page_list /*[in]*/,
      std::size_t layer_id /*[in]*/) = 0;

  virtual std::unique_ptr<TransferWork> AsyncRecv(
      std::size_t src_replica_id /*[in]*/,
      torch::Tensor const& page_tensor /*[out]*/,
      const std::vector<std::size_t>& page_list /*[in]*/,
      std::size_t layer_id /*[in]*/) = 0;
  virtual std::vector<std::size_t> GetMatchingOtherGlobalRanks(
      std::size_t other_replica_id /*[in]*/, std::size_t layer_id /*[in]*/) = 0;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
