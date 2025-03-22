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
#include "native/model_executor/layers/attention/AttentionWrapper.h"
//==============================================================================
namespace vajra {
class LlamaMLP {
 public:
  LlamaMLP(std::size_t layer_id /*[in]*/,
           ColumnParallelLinearPtr gate_up_proj /*[in]*/,
           RowParallelLinearPtr down_proj /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& input /*[in]*/) const;

 private:
  std::size_t layer_id_;
  ColumnParallelLinearPtr gate_up_proj_;
  RowParallelLinearPtr down_proj_;
};

using LlamaMLPPtr = std::shared_ptr<const LlamaMLP>;
//==============================================================================
class LlamaAttention {
 public:
  LlamaAttention(int q_size /*[in]*/, int kv_size /*[in]*/,
                 float scaling /*[in]*/, std::size_t layer_id /*[in]*/,
                 ColumnParallelLinearPtr qkv_proj /*[in]*/,
                 RowParallelLinearPtr o_proj /*[in]*/,
                 RotaryEmbeddingPtr rotary_emb /*[in]*/,
                 AttentionWrapperPtr attention_wrapper /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& positions,     /*[in]*/
                        const torch::Tensor& hidden_states, /*[in]*/
                        torch::Tensor& kv_cache             /*[inout]*/
  ) const;

 private:
  int q_size_;
  int kv_size_;
  float scaling_;
  std::size_t layer_id_;
  ColumnParallelLinearPtr qkv_proj_;
  RowParallelLinearPtr o_proj_;
  RotaryEmbeddingPtr rotary_emb_;
  AttentionWrapperPtr attention_wrapper_;
};

using LlamaAttentionPtr = std::shared_ptr<const LlamaAttention>;
//==============================================================================
class LlamaDecoderLayer {
 public:
  LlamaDecoderLayer(std::size_t layer_id /*[in]*/,
                    LlamaAttentionPtr self_attn /*[in]*/,
                    LlamaMLPPtr mlp /*[in]*/,
                    RMSNormPtr input_layernorm /*[in]*/,
                    RMSNormPtr post_attention_layernorm /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& positions, /*[in]*/
                        torch::Tensor& hidden_states,   /*[in]*/
                        torch::Tensor& kv_cache         /*[inout]*/
  ) const;

 private:
  std::size_t layer_id_;
  LlamaAttentionPtr self_attn_;
  LlamaMLPPtr mlp_;
  RMSNormPtr input_layernorm_;
  RMSNormPtr post_attention_layernorm_;
};

using LlamaDecoderLayerPtr = std::shared_ptr<const LlamaDecoderLayer>;
//==============================================================================
class LlamaModel {
 public:
  LlamaModel(VocabParallelEmbeddingPtr embed_tokens /*[in]*/,
             std::vector<LlamaDecoderLayerPtr> layers /*[in]*/,
             RMSNormPtr norm /*[in]*/);

  torch::Tensor Forward(const torch::Tensor& positions /*[in]*/,
                        torch::Tensor& hidden_states /*[in]*/,
                        std::vector<torch::Tensor> kv_caches /*[inout]*/
  );

 private:
  VocabParallelEmbeddingPtr embed_tokens_;
  std::vector<LlamaDecoderLayerPtr> layers_;
  RMSNormPtr norm_;
};

using LlamaModelPtr = std::shared_ptr<const LlamaModel>;
//==============================================================================
}  // namespace vajra
//==============================================================================
