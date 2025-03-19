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
#include "native/model_executor/layers/attention/SequenceArrangement.h"

#include "commons/Logging.h"
//==============================================================================
namespace vajra {
//==============================================================================
BaseSequenceArrangement::BaseSequenceArrangement(ContainerType r1 /*[in]*/,
                                                 ContainerType r2 /*[in]*/)
    : r1_(std::move(r1)), r2_(std::move(r2)) {}

void BaseSequenceArrangement::Append(
    std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) {
  if (CheckPredicate(seq_metadata)) {
    if (std::holds_alternative<SequenceMetadataVector>(r1_)) {
      std::get<SequenceMetadataVector>(r1_).push_back(seq_metadata);
    } else {
      std::get<std::shared_ptr<BaseSequenceArrangement>>(r1_)->Append(
          seq_metadata);
    }
  } else {
    if (std::holds_alternative<SequenceMetadataVector>(r2_)) {
      std::get<SequenceMetadataVector>(r2_).push_back(seq_metadata);
    } else {
      std::get<std::shared_ptr<BaseSequenceArrangement>>(r2_)->Append(
          seq_metadata);
    }
  }
}
//==============================================================================
void BaseSequenceArrangement::Extend(
    std::vector<std::shared_ptr<SequenceMetadata>> seq_metadata_list /*[in]*/) {
  for (const auto& seq_metadata : seq_metadata_list) {
    Append(seq_metadata);
  }
}
//==============================================================================
void BaseSequenceArrangement::CheckArrangementAndExtend(
    std::vector<std::shared_ptr<SequenceMetadata>> seq_metadata_list /*[in]*/) {
  bool started_r2 = false;
  SequenceMetadataVector r1_seq_metadata;
  SequenceMetadataVector r2_seq_metadata;

  for (const auto& seq_metadata : seq_metadata_list) {
    if (CheckPredicate(seq_metadata)) {
      ASSERT_VALID_RUNTIME(!started_r2, "Sequence metadata list is not sorted");
      r1_seq_metadata.push_back(seq_metadata);
    } else {
      started_r2 = true;
      r2_seq_metadata.push_back(seq_metadata);
    }
  }

  if (std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r1_) &&
      std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r2_)) {
    std::get<std::shared_ptr<BaseSequenceArrangement>>(r1_)
        ->CheckArrangementAndExtend(r1_seq_metadata);
    std::get<std::shared_ptr<BaseSequenceArrangement>>(r2_)
        ->CheckArrangementAndExtend(r2_seq_metadata);
  } else {
    if (std::holds_alternative<SequenceMetadataVector>(r1_)) {
      auto& r1_vec = std::get<SequenceMetadataVector>(r1_);
      r1_vec.insert(r1_vec.end(), r1_seq_metadata.begin(),
                    r1_seq_metadata.end());
    }
    if (std::holds_alternative<SequenceMetadataVector>(r2_)) {
      auto& r2_vec = std::get<SequenceMetadataVector>(r2_);
      r2_vec.insert(r2_vec.end(), r2_seq_metadata.begin(),
                    r2_seq_metadata.end());
    }
  }
}
//==============================================================================
std::vector<std::shared_ptr<SequenceMetadata>>
BaseSequenceArrangement::GetArranged() const {
  std::vector<std::shared_ptr<SequenceMetadata>> result;

  if (std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r1_) &&
      std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r2_)) {
    auto r1_arranged =
        std::get<std::shared_ptr<BaseSequenceArrangement>>(r1_)->GetArranged();
    auto r2_arranged =
        std::get<std::shared_ptr<BaseSequenceArrangement>>(r2_)->GetArranged();
    result.insert(result.end(), r1_arranged.begin(), r1_arranged.end());
    result.insert(result.end(), r2_arranged.begin(), r2_arranged.end());
  } else {
    ASSERT_VALID_RUNTIME(
        std::holds_alternative<SequenceMetadataVector>(r1_) &&
            std::holds_alternative<SequenceMetadataVector>(r2_),
        "Container types mismatch in GetArranged");
    const auto& r1_vec = std::get<SequenceMetadataVector>(r1_);
    const auto& r2_vec = std::get<SequenceMetadataVector>(r2_);
    result.insert(result.end(), r1_vec.begin(), r1_vec.end());
    result.insert(result.end(), r2_vec.begin(), r2_vec.end());
  }

  return result;
}
//==============================================================================
std::vector<std::vector<std::shared_ptr<SequenceMetadata>>>
BaseSequenceArrangement::GetSplits() const {
  std::vector<std::vector<std::shared_ptr<SequenceMetadata>>> result;

  if (std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r1_) &&
      std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r2_)) {
    auto r1_splits =
        std::get<std::shared_ptr<BaseSequenceArrangement>>(r1_)->GetSplits();
    auto r2_splits =
        std::get<std::shared_ptr<BaseSequenceArrangement>>(r2_)->GetSplits();
    result.insert(result.end(), r1_splits.begin(), r1_splits.end());
    result.insert(result.end(), r2_splits.begin(), r2_splits.end());
  } else {
    ASSERT_VALID_RUNTIME(
        std::holds_alternative<SequenceMetadataVector>(r1_) &&
            std::holds_alternative<SequenceMetadataVector>(r2_),
        "Container types mismatch in GetSplits");
    std::vector<std::shared_ptr<SequenceMetadata>> combined;
    const auto& r1_vec = std::get<SequenceMetadataVector>(r1_);
    const auto& r2_vec = std::get<SequenceMetadataVector>(r2_);
    combined.insert(combined.end(), r1_vec.begin(), r1_vec.end());
    combined.insert(combined.end(), r2_vec.begin(), r2_vec.end());
    result.push_back(std::move(combined));
  }

  return result;
}
//==============================================================================
int BaseSequenceArrangement::GetNumSplits() const {
  if (std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r1_) &&
      std::holds_alternative<std::shared_ptr<BaseSequenceArrangement>>(r2_)) {
    return std::get<std::shared_ptr<BaseSequenceArrangement>>(r1_)
               ->GetNumSplits() +
           std::get<std::shared_ptr<BaseSequenceArrangement>>(r2_)
               ->GetNumSplits();
  }
  ASSERT_VALID_RUNTIME(std::holds_alternative<SequenceMetadataVector>(r1_) &&
                           std::holds_alternative<SequenceMetadataVector>(r2_),
                       "Container types mismatch in GetNumSplits");
  return 1;
}
//==============================================================================
SequenceGroupArrangement::SequenceGroupArrangement()
    : BaseSequenceArrangement(SequenceMetadataVector(),
                              SequenceMetadataVector()) {}
//==============================================================================
bool SequenceGroupArrangement::CheckPredicate(
    std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const {
  return !seq_metadata->is_kvp_request;
}
//==============================================================================
SaveKvCacheBasedSequenceArrangement::SaveKvCacheBasedSequenceArrangement()
    : BaseSequenceArrangement(std::make_shared<SequenceGroupArrangement>(),
                              std::make_shared<SequenceGroupArrangement>()) {}
//==============================================================================
bool SaveKvCacheBasedSequenceArrangement::CheckPredicate(
    std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const {
  return seq_metadata->save_kv_cache;
}
//==============================================================================
LengthBasedSequenceArrangement::LengthBasedSequenceArrangement()
    : BaseSequenceArrangement(
          std::make_shared<SaveKvCacheBasedSequenceArrangement>(),
          std::make_shared<SaveKvCacheBasedSequenceArrangement>()) {}
//==============================================================================
bool LengthBasedSequenceArrangement::CheckPredicate(
    std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const {
  return seq_metadata->num_kv_tokens > LONG_REQUEST_THRESHOLD;
}
//==============================================================================
SequenceArrangement::SequenceArrangement()
    : BaseSequenceArrangement(
          std::make_shared<LengthBasedSequenceArrangement>(),
          std::make_shared<LengthBasedSequenceArrangement>()) {}
//==============================================================================
bool SequenceArrangement::CheckPredicate(
    std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const {
  return seq_metadata->num_q_tokens > 1;
}
//==============================================================================
}  // namespace vajra
//==============================================================================
