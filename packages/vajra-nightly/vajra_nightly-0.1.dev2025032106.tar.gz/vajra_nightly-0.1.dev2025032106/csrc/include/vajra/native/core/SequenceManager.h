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

#include <pybind11/pybind11.h>

#include <mutex>  // NOLINT

#include "commons/Logging.h"
#include "commons/StdCommon.h"
#include "native/datatypes/RequestOutput.h"
#include "native/datatypes/SamplerOutput.h"
#include "native/datatypes/SchedulerOutput.h"
#include "native/datatypes/Sequence.h"

namespace vajra {

class SequenceManager {
 public:
  explicit SequenceManager(bool enable_sequence_pipeline_parallel)
      : enable_sequence_pipeline_parallel_(enable_sequence_pipeline_parallel) {}

  virtual inline void AddSeq(MutableSequencePtr seq) {
    std::lock_guard<std::recursive_mutex> lk(mutex_);

    ASSERT_VALID_RUNTIME(seq_map_.find(seq->seq_id) == seq_map_.end(),
                         "sequence {} already added ", seq->seq_id);
    seq_map_[seq->seq_id] = seq;
  }

  virtual inline SequencePtr GetSeq(const std::string& seq_id) const {
    return seq_map_.at(seq_id);
  }

  virtual std::pair<Sequences, Sequences> OnSchedule(
      SchedulerOutputPtr scheduler_output);

  virtual void OnStepCompleted(const std::vector<SequenceScheduleMetadataPtr>&
                                   seq_schedule_metadata_list,
                               const SamplerOutputs& sampler_outputs);

  virtual void OnStageCompleted(SchedulerOutputPtr scheduler_output);

  virtual std::vector<RequestOutput> GenerateRequestOutputs(
      const Sequences& ignored_seqs, const Sequences& seqs);

 protected:
  virtual inline void FreeSeq(const std::string& seq_id) {
    ASSERT_VALID_RUNTIME(seq_map_.find(seq_id) != seq_map_.end(),
                         "sequence {} not found", seq_id);
    seq_map_.erase(seq_id);
  }

  virtual void PreemptSeq(const std::string& seq_id);

  virtual void PauseSeq(const std::string& seq_id);

  virtual void ResumeSeq(const std::string& seq_id);

  virtual inline void OnSeqScheduled(
      SequenceScheduleMetadataPtr seq_sched_metadata) {
    ResumeSeq(seq_sched_metadata->seq_id);
  }

  virtual std::vector<int> GetBlockTable(SequencePtr seq) const = 0;

  virtual void OnAppendToken(MutableSequencePtr seq,
                             std::size_t num_new_tokens) = 0;

  virtual void ProcessSeqOutput(MutableSequencePtr seq,
                                SamplerOutputPtr sample);

  std::unordered_map<std::string, MutableSequencePtr> seq_map_;
  bool enable_sequence_pipeline_parallel_;
  std::recursive_mutex mutex_;
};

// SequenceManager has pure virtual methods. pybind fails to generate bindings
// without explicitly marking them pure. Define a wrapper that marks them pure.
// See:
// https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
class PySequenceManager : SequenceManager {
  using SequenceManager::SequenceManager;

  std::vector<int> GetBlockTable(SequencePtr) const override {
    PYBIND11_OVERRIDE_PURE(std::vector<int>, SequenceManager, GetBlockTable);
  }

  void OnAppendToken(MutableSequencePtr, std::size_t) override {
    PYBIND11_OVERRIDE_PURE(void, SequenceManager, OnAppendToken);
  }
};
}  // namespace vajra
