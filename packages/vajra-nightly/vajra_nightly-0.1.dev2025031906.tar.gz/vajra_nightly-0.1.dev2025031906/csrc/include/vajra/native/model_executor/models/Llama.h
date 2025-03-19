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
#include "native/model_executor/layers/LinearLayers.h"
#include "native/model_executor/layers/NormLayers.h"
#include "native/model_executor/layers/RotaryEmbedding.h"
//==============================================================================
namespace vajra {
class LlamaMLP {
 public:
  LlamaMLP(const std::shared_ptr<ColumnParallelLinear> gate_up_proj /*[in]*/,
           const std::shared_ptr<RowParallelLinear> down_proj /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& input /*[in]*/) const;

 private:
  const std::shared_ptr<ColumnParallelLinear> gate_up_proj_;
  const std::shared_ptr<RowParallelLinear> down_proj_;
};
//==============================================================================
class LlamaAttention {
 public:
  LlamaAttention(int q_size /*[in]*/, int kv_size /*[in]*/,
                 float scaling /*[in]*/,
                 const std::shared_ptr<ColumnParallelLinear> qkv_proj /*[in]*/,
                 const std::shared_ptr<RowParallelLinear> o_proj /*[in]*/,
                 const std::shared_ptr<RotaryEmbedding> rotary_emb /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& positions,     /*[in]*/
                        const torch::Tensor& hidden_states, /*[in]*/
                        torch::Tensor& kv_cache             /*[inout]*/
  ) const;

 private:
  int q_size_;
  int kv_size_;
  float scaling_;
  const std::shared_ptr<ColumnParallelLinear> qkv_proj_;
  const std::shared_ptr<RowParallelLinear> o_proj_;
  const std::shared_ptr<RotaryEmbedding> rotary_emb_;
};
//==============================================================================
class LlamaDecoderLayer {
 public:
  LlamaDecoderLayer(
      const std::shared_ptr<LlamaAttention> self_attn /*[in]*/,
      const std::shared_ptr<LlamaMLP> mlp /*[in]*/,
      const std::shared_ptr<RMSNorm> input_layernorm /*[in]*/,
      const std::shared_ptr<RMSNorm> post_attention_layernorm /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& positions, /*[in]*/
                        torch::Tensor& hidden_states,   /*[in]*/
                        torch::Tensor& kv_cache         /*[inout]*/
  ) const;

 private:
  const std::shared_ptr<LlamaAttention> self_attn_;
  const std::shared_ptr<LlamaMLP> mlp_;
  const std::shared_ptr<RMSNorm> input_layernorm_;
  const std::shared_ptr<RMSNorm> post_attention_layernorm_;
};
//==============================================================================
class LlamaModel {
 public:
  LlamaModel(
      const std::shared_ptr<VocabParallelEmbedding> embed_tokens /*[in]*/,
      const std::vector<std::shared_ptr<LlamaDecoderLayer>> layers /*[in]*/,
      const std::shared_ptr<RMSNorm> norm /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& positions /*[in]*/,
                        torch::Tensor& hidden_states /*[in]*/,
                        std::vector<torch::Tensor> kv_caches /*[inout]*/
  );

 private:
  const std::shared_ptr<VocabParallelEmbedding> embed_tokens_;
  const std::vector<std::shared_ptr<LlamaDecoderLayer>> layers_;
  const std::shared_ptr<RMSNorm> norm_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
