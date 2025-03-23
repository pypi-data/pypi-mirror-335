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
#include "native/engine/InferenceEngine.h"
//==============================================================================
namespace vajra {
//==============================================================================
void InferenceEngine::AddRequest(const std::string& seq_id,
                                 const std::string& prompt,
                                 const TokenIdsPtr prompt_token_ids,
                                 const double arrival_time,
                                 const SamplingParams& sampling_params) {
  // Create a shared_ptr to UserSequenceParams
  auto params = std::make_shared<const UserSequenceParams>(
      seq_id, prompt, prompt_token_ids, arrival_time, sampling_params);
  waiting_seq_queue_->push(params);
  metrics_store_->OnRequestArrival(seq_id, arrival_time);
}
//==============================================================================
std::vector<RequestOutput> InferenceEngine::GetOutputs(const bool block) const {
  std::vector<RequestOutput> outputs;
  std::shared_ptr<RequestOutput> item_ptr;

  if (block) {
    try {
      // Use try_pull with proper status checking instead of pull_front
      boost::concurrent::queue_op_status status =
          output_queue_->try_pull(item_ptr);
      if (status == boost::concurrent::queue_op_status::success && item_ptr) {
        outputs.push_back(*item_ptr);  // Dereference the pointer
      } else if (status == boost::concurrent::queue_op_status::closed) {
        return outputs;
      }
    } catch (const boost::sync_queue_is_closed& e) {
      return outputs;
    }
  }

  // Non-blocking drain of remaining items
  while (true) {
    try {
      boost::concurrent::queue_op_status status =
          output_queue_->try_pull(item_ptr);
      if (status == boost::concurrent::queue_op_status::success && item_ptr) {
        outputs.push_back(*item_ptr);  // Dereference the pointer
      } else if (status == boost::concurrent::queue_op_status::empty ||
                 status == boost::concurrent::queue_op_status::closed) {
        break;
      }
    } catch (const boost::sync_queue_is_closed& e) {
      break;
    }
  }
  return outputs;
}
//==============================================================================
}  // namespace vajra
//==============================================================================
