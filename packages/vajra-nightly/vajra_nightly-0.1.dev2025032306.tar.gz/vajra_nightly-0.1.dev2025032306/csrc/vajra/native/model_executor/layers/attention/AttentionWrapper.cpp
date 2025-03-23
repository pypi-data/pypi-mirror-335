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
#include "native/model_executor/layers/attention/AttentionWrapper.h"
//==============================================================================
using vajra::AttentionWrapper;
//==============================================================================
AttentionWrapper::AttentionWrapper(std::size_t num_q_heads /*[in]*/,
                                   std::size_t num_kv_heads /*[in]*/,
                                   std::size_t head_dim /*[in]*/,
                                   std::size_t block_size /*[in]*/,
                                   torch::Device device /*[in]*/)
    : num_q_heads_(num_q_heads),
      num_kv_heads_(num_kv_heads),
      head_dim_(head_dim),
      block_size_(block_size),
      device_(device),
      is_metadata_initialized_(false),
      is_profiling_iteration_(false) {
  std::size_t num_sequence_splits = sequence_arrangement_.GetNumSplits();
  LOG_INFO("Creating {} native FlashinferAttentionWrapper instances.",
           num_sequence_splits);

  for (std::size_t i = 0; i < num_sequence_splits; ++i) {
    wrappers_.emplace_back(num_q_heads, num_kv_heads, head_dim, block_size,
                           device);
  }
}
//==============================================================================
void AttentionWrapper::BeginForward(
    SequenceMetadataVector seq_metadata_list /*[in]*/) {
  ASSERT_VALID_RUNTIME(!is_metadata_initialized_,
                       "Metadata already initialized. Call EndForward first.");
  is_metadata_initialized_ = true;
  is_profiling_iteration_ = false;

  if (seq_metadata_list.empty() || seq_metadata_list[0]->block_table.empty()) {
    is_profiling_iteration_ = true;
    return;
  }

  sequence_arrangement_.CheckArrangementAndExtend(seq_metadata_list);
  auto split_seq_metadata_list = sequence_arrangement_.GetSplits();

  ASSERT_VALID_RUNTIME(split_seq_metadata_list.size() == wrappers_.size(),
                       "Invalid number of splits. Expected: {} Got: {}",
                       wrappers_.size(), split_seq_metadata_list.size());
  for (std::size_t i = 0; i < split_seq_metadata_list.size(); ++i) {
    wrappers_[i].BeginForward(split_seq_metadata_list[i]);
  }
}
//==============================================================================
void AttentionWrapper::EndForward() {
  ASSERT_VALID_RUNTIME(is_metadata_initialized_,
                       "Metadata not initialized. Call BeginForward first.");
  is_metadata_initialized_ = false;

  if (is_profiling_iteration_) {
    return;
  }

  for (auto& wrapper : wrappers_) {
    wrapper.EndForward();
  }

  sequence_arrangement_.Clear();
}
//==============================================================================
torch::Tensor AttentionWrapper::Forward(const torch::Tensor& query /*[in]*/,
                                        const torch::Tensor& key /*[in]*/,
                                        const torch::Tensor& value /*[in]*/,
                                        torch::Tensor& kv_cache /*[inout]*/,
                                        std::size_t layer_id /*[in]*/) {
  ASSERT_VALID_RUNTIME(is_metadata_initialized_,
                       "Metadata not initialized. Call BeginForward first.");

  if (is_profiling_iteration_) {
    return torch::empty_like(query);
  }

  auto output = torch::empty(
      {query.size(0), num_q_heads_, head_dim_},
      torch::TensorOptions().dtype(query.dtype()).device(query.device()));

  auto logsumexp = torch::empty(
      {query.size(0), num_q_heads_},
      torch::TensorOptions().dtype(torch::kFloat32).device(query.device()));

  // Reshape inputs ATTN_INPUT_RESHAPE
  auto query_reshaped = query.reshape({-1, num_q_heads_, head_dim_});
  auto key_reshaped = key.reshape({-1, num_kv_heads_, head_dim_});
  auto value_reshaped = value.reshape({-1, num_kv_heads_, head_dim_});

  // Save kv_cache ATTN_KV_CACHE_SAVE
  {
    std::size_t q_offset = 0;
    for (auto& wrapper : wrappers_) {
      std::size_t q_len = wrapper.GetNumQTokens();

      if (q_len == 0) {
        continue;
      }

      wrapper.SaveKVCache(key_reshaped.slice(0, q_offset, q_offset + q_len),
                          value_reshaped.slice(0, q_offset, q_offset + q_len),
                          kv_cache);

      q_offset += q_len;
    }
  }

  // Attention computation ATTN
  {
    std::size_t q_offset = 0;
    for (auto& wrapper : wrappers_) {
      std::size_t q_len = wrapper.GetNumQTokens();

      if (q_len == 0) {
        continue;
      }

      auto output_slice = output.slice(0, q_offset, q_offset + q_len);
      auto logsumexp_slice = logsumexp.slice(0, q_offset, q_offset + q_len);

      wrapper.Run(query_reshaped.slice(0, q_offset, q_offset + q_len),
                  output_slice, logsumexp_slice, kv_cache);

      q_offset += q_len;
    }
  }

  // Reshape outputs ATTN_OUTPUT_RESHAPE
  auto output_reshaped = output.reshape({-1, num_q_heads_ * head_dim_});

  return output_reshaped;
}
//==============================================================================
