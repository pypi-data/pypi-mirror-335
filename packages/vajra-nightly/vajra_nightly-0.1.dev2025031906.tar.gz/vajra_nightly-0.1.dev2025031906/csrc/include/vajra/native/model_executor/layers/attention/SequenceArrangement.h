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

#include "commons/StdCommon.h"
#include "native/datatypes/SequenceMetadata.h"
//==============================================================================
namespace vajra {
//==============================================================================

constexpr int64_t LONG_REQUEST_THRESHOLD = 256 * 1024;  // 256K

class BaseSequenceArrangement;
using ContainerType =
    std::variant<std::vector<std::shared_ptr<SequenceMetadata>>,
                 std::shared_ptr<BaseSequenceArrangement>>;

// Type alias for the complex std::holds_alternative expression
using SequenceMetadataVector = std::vector<std::shared_ptr<SequenceMetadata>>;

class BaseSequenceArrangement {
 public:
  virtual ~BaseSequenceArrangement() = default;

  void Append(std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/);
  void Extend(std::vector<std::shared_ptr<SequenceMetadata>>
                  seq_metadata_list /*[in]*/);
  void CheckArrangementAndExtend(std::vector<std::shared_ptr<SequenceMetadata>>
                                     seq_metadata_list /*[in]*/);
  std::vector<std::shared_ptr<SequenceMetadata>> GetArranged() const;
  std::vector<std::vector<std::shared_ptr<SequenceMetadata>>> GetSplits() const;
  int GetNumSplits() const;

 protected:
  BaseSequenceArrangement(ContainerType r1 /*[in]*/, ContainerType r2 /*[in]*/);
  virtual bool CheckPredicate(
      std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const = 0;

  ContainerType r1_;
  ContainerType r2_;
};

class SequenceGroupArrangement : public BaseSequenceArrangement {
 public:
  SequenceGroupArrangement();

 protected:
  bool CheckPredicate(
      std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const override;
};

class SaveKvCacheBasedSequenceArrangement : public BaseSequenceArrangement {
 public:
  SaveKvCacheBasedSequenceArrangement();

 protected:
  bool CheckPredicate(
      std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const override;
};

class LengthBasedSequenceArrangement : public BaseSequenceArrangement {
 public:
  LengthBasedSequenceArrangement();

 protected:
  bool CheckPredicate(
      std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const override;
};

class SequenceArrangement : public BaseSequenceArrangement {
 public:
  SequenceArrangement();

 protected:
  bool CheckPredicate(
      std::shared_ptr<SequenceMetadata> seq_metadata /*[in]*/) const override;
};

//==============================================================================
}  // namespace vajra
//==============================================================================
