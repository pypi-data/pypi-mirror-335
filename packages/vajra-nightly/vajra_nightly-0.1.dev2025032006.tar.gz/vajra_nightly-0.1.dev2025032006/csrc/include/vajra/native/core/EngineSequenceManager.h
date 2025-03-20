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

#include "native/core/SequenceManager.h"
#include "native/core/Tokenizer.h"

namespace vajra {

class EngineSequenceManager : public SequenceManager {
 public:
  EngineSequenceManager(std::shared_ptr<Tokenizer> tokenizer,
                        bool enable_sequence_pipeline_parallel)
      : SequenceManager(enable_sequence_pipeline_parallel),
        tokenizer_(tokenizer) {}

 protected:
  inline std::vector<int> GetBlockTable(SequencePtr) const override {
    return std::vector<int>();
  }

  void OnAppendToken(MutableSequencePtr seq,
                     std::size_t num_new_tokens) override;

 private:
  std::shared_ptr<Tokenizer> tokenizer_;
};

}  // namespace vajra
