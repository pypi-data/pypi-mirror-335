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
//==============================================================================
#include "commons/BoostCommon.h"
#include "native/datatypes/BaseSequenceWithPriority.h"
//==============================================================================
namespace vajra {
//==============================================================================
class BaseReplicaScheduler {
 public:
  BaseReplicaScheduler(
      const ModelConfig& model_config,
      const BaseReplicaSchedulerConfig& scheduler_config,
      const CacheConfig& cache_config, const ParallelConfig& parallel_config,
      std::size_t num_gpu_blocks, SequencePriorityQueuePtr waiting_queue,
      std::shared_ptr<BaseRequestPrioritizer> request_prioritizer);

  virtual ~BaseReplicaScheduler() = default;

  // Reset the internal state
  void ResetState();

  // Add sequence to the partial prefill queue
  void AddPartialPrefill(const MutableSequencePtr& seq);

  // Called when a stage is completed
  void OnStageCompleted(const MutableSequences& seqs);

  // Called when a step is completed
  void OnStepCompleted(const MutableSequences& seqs, float execution_time);

  // Schedule the next batch
  [[nodiscard]] virtual std::pair<std::shared_ptr<SchedulerOutput>,
                                  MutableSequences>
  Schedule() = 0;

  // Free finished sequences
  void FreeFinishedSeqs();

  // Check if sequence is allocated
  bool IsSeqAllocated(const std::string& seq_id) const;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
