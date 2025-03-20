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

#include "commons/Logging.h"
#include "commons/StdCommon.h"
#include "native/datatypes/LogicalTokenBlock.h"
#include "native/datatypes/SamplingParams.h"
#include "native/datatypes/SequenceState.h"

namespace vajra {

using TokenId = std::int32_t;

struct SequenceParams {
  SequenceParams(const std::string seq_id_param, const std::string prompt_param,
                 const std::vector<TokenId> prompt_token_ids_param,
                 const std::size_t block_size_param,
                 const TokenId eos_token_id_param,
                 const double arrival_time_param,
                 const SamplingParams sampling_params_param)
      : seq_id(seq_id_param),
        prompt(prompt_param),
        prompt_token_ids(prompt_token_ids_param),
        block_size(block_size_param),
        eos_token_id(eos_token_id_param),
        arrival_time(arrival_time_param),
        sampling_params(sampling_params_param) {}

  const std::string seq_id;
  const std::string prompt;
  const std::vector<TokenId> prompt_token_ids;
  const std::size_t block_size;
  const TokenId eos_token_id;
  const double arrival_time;
  const SamplingParams sampling_params;
};

class Sequence {
 public:
  Sequence(const std::string seq_id_param, const std::string prompt_param,
           const std::vector<TokenId> prompt_token_ids_param,
           const std::size_t block_size_param, const TokenId eos_token_id_param,
           const double arrival_time_param,
           const SamplingParams sampling_params_param);

  explicit Sequence(const SequenceParams& params)
      : Sequence(params.seq_id, params.prompt, params.prompt_token_ids,
                 params.block_size, params.eos_token_id, params.arrival_time,
                 params.sampling_params) {}

  inline SequenceStatus GetStatus() const { return state_.GetStatus(); }

  inline void SetStatus(SequenceStatus status /*[in]*/) {
    state_.SetStatus(status);
  }

  inline const std::vector<TokenId>& GetPromptTokenIds() const {
    return prompt_token_ids_;
  }

  inline const std::vector<TokenId>& GetOutputTokenIds() const {
    return output_token_ids_;
  }

  inline const std::vector<std::shared_ptr<vajra::LogicalTokenBlock>>&
  GetLogicalTokenBlocks() const {
    return logical_token_blocks_;
  }

  inline bool GetPromptProcessingFinished() const {
    return prompt_processing_finished_;
  }

  inline bool GetPromptStageProcessingFinished() const {
    return prompt_stage_processing_finished_;
  }

  inline const SequenceState& GetState() const { return state_; }

  void UpdatePromptTokensProcessed(std::size_t num_tokens /*[in]*/);

  void UpdatePromptTokensStageProcessed(std::size_t num_tokens /*[in]*/);

  void AppendTokenId(TokenId token_id /*[in]*/);

  inline std::size_t Length() const {
    return output_token_ids_.size() + prompt_token_ids_.size();
  }

  inline std::size_t GetPromptLength() const {
    return prompt_token_ids_.size();
  }

  inline std::size_t GetOutputLength() const {
    return output_token_ids_.size();
  }

  inline std::size_t GetNumPromptTokensProcessed() const {
    return prompt_tokens_processed_;
  }

  inline std::size_t GetNumPromptTokensStageProcessed() const {
    return prompt_tokens_stage_processed_;
  }

  inline std::size_t GetNumTokensProcessed() const {
    return prompt_tokens_processed_ + output_token_ids_.size();
  }

  inline std::size_t GetNumTokensStageProcessed() const

  {
    return prompt_tokens_stage_processed_ + output_token_ids_.size();
  }

  inline std::size_t GetLastTokenId() const {
    return output_token_ids_.size() > 0 ? output_token_ids_.back()
                                        : prompt_token_ids_.back();
  }

  std::vector<TokenId> GetLastNTokenIds(std::size_t n /*[in]*/,
                                        bool truncate = false) const;

  inline const std::vector<std::string>& GetTokens() const { return tokens_; }

  inline void SetTokens(const std::vector<std::string>& tokens /*[in]*/) {
    tokens_ = tokens;
  }

  inline void ExtendTokens(const std::vector<std::string>& tokens /*[in]*/) {
    tokens_.insert(tokens_.end(), tokens.begin(), tokens.end());
  }

  inline bool IsFinished() const {
    return sequence_status::IsFinished(state_.GetStatus());
  }
  inline bool IsExecuting() const {
    return sequence_status::IsExecuting(state_.GetStatus());
  }
  inline bool IsWaiting() const {
    return sequence_status::IsWaiting(state_.GetStatus());
  }
  inline bool IsPaused() const {
    return sequence_status::IsPaused(state_.GetStatus());
  }
  inline bool IsRunning() const {
    return sequence_status::IsRunning(state_.GetStatus());
  }
  inline bool IsWaitingPreempted() const {
    return sequence_status::IsWaitingPreempted(state_.GetStatus());
  }

  void Reset();

  void CheckStop(std::size_t num_new_tokens /*[in]*/);

  std::string ToString() {
    return fmt::format(
        "Sequence(seq_id={}, "
        "status={}, "
        "num_blocks={}, "
        "num_prompt_tokens={}, "
        "num_output_tokens={}, "
        "prompt_processing_finished={}, "
        "num_prompt_tokens_processed={}, "
        "num_prompt_tokens_stage_processed={}, "
        "prompt_stage_processing_finished={})",
        seq_id, GetStatus(), logical_token_blocks_.size(), GetPromptLength(),
        GetOutputLength(), prompt_processing_finished_,
        GetNumPromptTokensProcessed(), GetNumPromptTokensStageProcessed(),
        prompt_stage_processing_finished_);
  }

  const std::string seq_id;
  const std::string prompt;
  const std::size_t block_size;
  const TokenId eos_token_id;
  const double arrival_time;
  const SamplingParams sampling_params;

  std::string output_text;

  std::size_t prefix_offset = 0;
  std::size_t read_offset = 0;

 private:
  void AppendLogicalBlock();

  void AppendTokensToBlocks(const std::vector<TokenId>& token_ids /*[in]*/);

  std::vector<TokenId> prompt_token_ids_;
  std::vector<TokenId> output_token_ids_;
  std::size_t prompt_tokens_processed_ = 0;
  std::size_t prompt_tokens_stage_processed_ = 0;
  bool prompt_processing_finished_ = false;
  bool prompt_stage_processing_finished_ = false;

  std::vector<std::shared_ptr<vajra::LogicalTokenBlock>> logical_token_blocks_;
  SequenceState state_;
  std::vector<std::string> tokens_;
};

using SequencePtr = std::shared_ptr<const Sequence>;
using Sequences = std::vector<SequencePtr>;

using MutableSequencePtr = std::shared_ptr<Sequence>;
using MutableSequences = std::vector<MutableSequencePtr>;

class SequenceWithPriority {
 public:
  SequenceWithPriority(std::pair<double, double> priority, SequencePtr seq)
      : priority_(priority), seq_(seq) {}

  bool operator<(const SequenceWithPriority& other) const {
    return priority_ < other.priority_;
  }

  const std::pair<double, double>& GetPriority() const { return priority_; }
  SequencePtr GetSequence() const { return seq_; }

 private:
  std::pair<double, double> priority_;
  SequencePtr seq_;
};

}  // namespace vajra
