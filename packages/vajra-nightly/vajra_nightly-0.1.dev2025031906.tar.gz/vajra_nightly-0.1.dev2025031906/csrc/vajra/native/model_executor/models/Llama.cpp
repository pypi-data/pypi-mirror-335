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
#include "native/model_executor/models/Llama.h"

#include "kernels/ops.h"
//==============================================================================
using vajra::LlamaAttention;
using vajra::LlamaDecoderLayer;
using vajra::LlamaMLP;
using vajra::LlamaModel;
//==============================================================================
LlamaMLP::LlamaMLP(
    const std::shared_ptr<ColumnParallelLinear> gate_up_proj /*[in]*/,
    const std::shared_ptr<RowParallelLinear> down_proj /*[in]*/)
    : gate_up_proj_(gate_up_proj), down_proj_(down_proj) {
  ASSERT_VALID_RUNTIME(gate_up_proj_, "GateUpProj is null");
  ASSERT_VALID_RUNTIME(down_proj_, "DownProj is null");
}
//==============================================================================
torch::Tensor LlamaMLP::Forward(const torch::Tensor& input /*[in]*/) const {
  auto gate_up = gate_up_proj_->Forward(input);
  int num_tokens = input.size(0);
  int output_embedding_size = gate_up.size(1) / 2;
  auto activated =
      torch::empty({num_tokens, output_embedding_size}, input.options());
  silu_and_mul(activated, gate_up);
  return down_proj_->Forward(activated);
}
//==============================================================================
LlamaAttention::LlamaAttention(
    int q_size /*[in]*/, int kv_size /*[in]*/, float scaling /*[in]*/,
    const std::shared_ptr<ColumnParallelLinear> qkv_proj /*[in]*/,
    const std::shared_ptr<RowParallelLinear> o_proj /*[in]*/,
    const std::shared_ptr<RotaryEmbedding> rotary_emb /*[in]*/)
    : q_size_(q_size),
      kv_size_(kv_size),
      scaling_(scaling),
      qkv_proj_(qkv_proj),
      o_proj_(o_proj),
      rotary_emb_(rotary_emb) {
  ASSERT_VALID_RUNTIME(qkv_proj_, "QkvProj is null");
  ASSERT_VALID_RUNTIME(o_proj_, "OProj is null");
  ASSERT_VALID_RUNTIME(rotary_emb_, "RotaryEmb is null");
}
// ============================================================================
torch::Tensor LlamaAttention::Forward(
    const torch::Tensor& positions,     /*[in]*/
    const torch::Tensor& hidden_states, /*[in]*/
    torch::Tensor& kv_cache             /*[inout]*/
) const {
  auto qkv = qkv_proj_->Forward(hidden_states);
  auto qkv_split = torch::split(qkv, {q_size_, kv_size_, kv_size_}, -1);
  auto q = qkv_split[0];
  auto k = qkv_split[1];
  auto v = qkv_split[2];

  rotary_emb_->Forward(positions, q, k);

  // TODO(Amey): Add back the the call to attention wrapper
  // auto attn_output = attention_wrapper_->Forward(scaling_, q, k, v,
  // kv_cache); return o_proj_->Forward(attn_output);

  return hidden_states;
}
//==============================================================================
LlamaDecoderLayer::LlamaDecoderLayer(
    const std::shared_ptr<LlamaAttention> self_attn /*[in]*/,
    const std::shared_ptr<LlamaMLP> mlp /*[in]*/,
    const std::shared_ptr<RMSNorm> input_layernorm /*[in]*/,
    const std::shared_ptr<RMSNorm> post_attention_layernorm /*[in]*/)
    : self_attn_(self_attn),
      mlp_(mlp),
      input_layernorm_(input_layernorm),
      post_attention_layernorm_(post_attention_layernorm) {
  ASSERT_VALID_RUNTIME(self_attn_, "SelfAttn is null");
  ASSERT_VALID_RUNTIME(mlp_, "MLP is null");
  ASSERT_VALID_RUNTIME(input_layernorm_, "InputLayernorm is null");
  ASSERT_VALID_RUNTIME(post_attention_layernorm_,
                       "PostAttentionLayernorm is null");
}
//==============================================================================
torch::Tensor LlamaDecoderLayer::Forward(
    const torch::Tensor& positions, /*[in]*/
    torch::Tensor& hidden_states,   /*[in]*/
    torch::Tensor& kv_cache         /*[inout]*/
) const {
  auto residual = hidden_states;
  hidden_states = input_layernorm_->Forward(hidden_states);
  hidden_states = self_attn_->Forward(positions, hidden_states, kv_cache);
  hidden_states = residual + hidden_states;

  residual = hidden_states;
  hidden_states = post_attention_layernorm_->Forward(hidden_states);
  hidden_states = mlp_->Forward(hidden_states);
  hidden_states = residual + hidden_states;

  return hidden_states;
}
//==============================================================================
LlamaModel::LlamaModel(
    const std::shared_ptr<VocabParallelEmbedding> embed_tokens /*[in]*/,
    const std::vector<std::shared_ptr<LlamaDecoderLayer>> layers /*[in]*/,
    const std::shared_ptr<RMSNorm> norm /*[in]*/)
    : embed_tokens_(embed_tokens), layers_(layers), norm_(norm) {
  ASSERT_VALID_RUNTIME(layers_.size() > 0, "No layers provided");
}
//==============================================================================
torch::Tensor LlamaModel::Forward(
    const torch::Tensor& positions /*[in]*/,
    torch::Tensor& hidden_states /*[in]*/,
    std::vector<torch::Tensor> kv_caches /*[inout]*/
) {
  ASSERT_VALID_RUNTIME(kv_caches.size() == layers_.size(),
                       "KV cache size {} does not match number of layers {}",
                       kv_caches.size(), layers_.size());

  if (embed_tokens_) {
    hidden_states = embed_tokens_->Forward(hidden_states);
  }

  for (std::size_t i = 0; i < layers_.size(); i++) {
    hidden_states = layers_[i]->Forward(positions, hidden_states, kv_caches[i]);
  }

  if (norm_) {
    hidden_states = norm_->Forward(hidden_states);
  }

  return hidden_states;
}
//==============================================================================
