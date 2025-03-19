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
#include "native/core/WorkerSequenceManager.h"

#include "native/model_executor/layers/attention/SequenceArrangement.h"

namespace vajra {
WorkerSequenceManager::WorkerSequenceManager(WorkerSequenceManagerParams params)
    : SequenceManager(params.enable_sequence_pipeline_parallel),
      rank_(params.rank),
      kvp_group_id_(params.kvp_group_id),
      block_manager_(BlockSpaceManager(params.block_size, params.num_gpu_blocks,
                                       params.max_model_len)) {
  if (params.kvp_parallel_world_size == 1) {
    max_num_tokens_per_kvp_group_ = params.max_model_len;
  } else {
    max_num_tokens_per_kvp_group_ = params.max_num_tokens_per_kvp_group;
  }
}

void WorkerSequenceManager::OnStageCompleted(
    SchedulerOutputPtr scheduler_output) {
  std::lock_guard<std::recursive_mutex> lk(mutex_);

  if (!enable_sequence_pipeline_parallel_) return;

  for (auto metadata : scheduler_output->seq_schedule_metadata_list) {
    auto seq = seq_map_[metadata->seq_id];
    ASSERT_VALID_RUNTIME(!seq->IsFinished(), "seq {} has finished!",
                         seq->seq_id);

    if (seq->IsWaitingPreempted()) continue;

    if (seq->GetPromptStageProcessingFinished()) continue;

    UpdateSeqNumProcessedTokens(seq, metadata);

    seq->UpdatePromptTokensStageProcessed(metadata->num_q_tokens);

    bool kvp_group_id_found =
        std::find(metadata->kvp_group_ids.begin(),
                  metadata->kvp_group_ids.end(),
                  kvp_group_id_) != metadata->kvp_group_ids.end();
    if (kvp_group_id_found && !seq->GetPromptStageProcessingFinished())
      PauseSeq(metadata->seq_id);
  }
}

void WorkerSequenceManager::OnStepCompleted(
    const std::vector<SequenceScheduleMetadataPtr>& seq_schedule_metadata_list,
    const SamplerOutputs& sampler_outputs) {
  std::lock_guard<std::recursive_mutex> lk(mutex_);

  std::vector<SequenceScheduleMetadataPtr> filtered_seq_metadata;
  SamplerOutputs sorted_sampler_outputs;

  std::unordered_map<std::string, SamplerOutputPtr> sampler_outputs_map;
  for (auto s : sampler_outputs) {
    if (s.has_value()) {
      auto so = s.value();
      sampler_outputs_map[so->GetSeqId()] = so;
    }
  }

  for (auto metadata : seq_schedule_metadata_list) {
    auto seq = seq_map_[metadata->seq_id];
    ASSERT_VALID_RUNTIME(!seq->IsFinished(), "seq {} has finished!",
                         seq->seq_id);

    bool kvp_group_id_found =
        std::find(metadata->kvp_group_ids.begin(),
                  metadata->kvp_group_ids.end(),
                  kvp_group_id_) != metadata->kvp_group_ids.end();
    if (!kvp_group_id_found && !seq->GetPromptProcessingFinished()) {
      if (!enable_sequence_pipeline_parallel_) {
        seq->UpdatePromptTokensStageProcessed(metadata->num_q_tokens);
      }
      seq->UpdatePromptTokensProcessed(metadata->num_q_tokens);
      continue;
    }

    if (!enable_sequence_pipeline_parallel_ ||
        seq->GetPromptProcessingFinished()) {
      UpdateSeqNumProcessedTokens(seq, metadata);
    }

    if (std::find(metadata->kvp_group_ids.begin(),
                  metadata->kvp_group_ids.end(),
                  kvp_group_id_) == metadata->kvp_group_ids.end()) {
      continue;
    }

    filtered_seq_metadata.emplace_back(metadata);
    sorted_sampler_outputs.emplace_back(sampler_outputs_map[seq->seq_id]);
  }

  SequenceManager::OnStepCompleted(filtered_seq_metadata,
                                   sorted_sampler_outputs);
}

std::pair<Sequences, Sequences> WorkerSequenceManager::OnSchedule(
    SchedulerOutputPtr) {
  ASSERT_VALID_RUNTIME(false,
                       "OnScheduler not implemented by WorkerSequenceManager");
}

std::tuple<Sequences, Sequences, std::vector<SequenceMetadataPtr>>
WorkerSequenceManager::OnScheduleWorker(SchedulerOutputPtr scheduler_output) {
  std::lock_guard<std::recursive_mutex> lk(mutex_);

  Sequences ignored_seqs;
  for (auto seq_id : scheduler_output->ignored_seq_ids) {
    ASSERT_VALID_RUNTIME(seq_map_.find(seq_id) != seq_map_.end(),
                         "sequence {} not found", seq_id);
    auto seq = seq_map_[seq_id];
    ignored_seqs.emplace_back(seq);
    FreeSeq(seq_id);
  }

  for (auto seq_id : scheduler_output->preempted_seq_ids) {
    PreemptSeq(seq_id);
  }

  std::vector<std::shared_ptr<SequenceMetadata>> seq_metadata_list;
  for (auto metadata : scheduler_output->seq_schedule_metadata_list) {
    ASSERT_VALID_RUNTIME(seq_map_.find(metadata->seq_id) != seq_map_.end(),
                         "seq_id {} not found in seq_map"
                         "seq_map: {} for rank {}",
                         metadata->seq_id, rank_);

    bool kvp_group_id_found =
        std::find(metadata->kvp_group_ids.begin(),
                  metadata->kvp_group_ids.end(),
                  kvp_group_id_) != metadata->kvp_group_ids.end();
    if (!kvp_group_id_found) continue;

    auto seq = seq_map_[metadata->seq_id];
    OnSeqScheduled(metadata);

    auto kv_cache_len = seq_num_processed_tokens_[seq->seq_id];
    auto save_kv_cache = kvp_group_id_ == metadata->kvp_group_ids.back();

    auto seq_metadata = std::make_shared<SequenceMetadata>(SequenceMetadata(
        metadata->schedule_id, seq->seq_id, metadata->num_q_tokens,
        kv_cache_len, GetBlockTable(seq), metadata->kvp_group_ids,
        save_kv_cache));
    seq_metadata_list.emplace_back(seq_metadata);
  }

  auto seq_arrangement = SequenceArrangement();
  seq_arrangement.Extend(seq_metadata_list);
  seq_metadata_list = seq_arrangement.GetArranged();

  Sequences seqs;
  seqs.reserve(seq_metadata_list.size());
  for (auto metadata : seq_metadata_list) {
    seqs.emplace_back(seq_map_[metadata->seq_id]);
  }

  return std::make_tuple(ignored_seqs, seqs, seq_metadata_list);
}

void WorkerSequenceManager::FreeSeq(const std::string& seq_id) {
  ASSERT_VALID_RUNTIME(seq_map_.find(seq_id) != seq_map_.end(),
                       "sequence {} not found", seq_id);
  auto seq = seq_map_[seq_id];
  if (block_manager_.IsAllocated(seq)) {
    block_manager_.Free(seq);
  }
  SequenceManager::FreeSeq(seq_id);
}

void WorkerSequenceManager::PreemptSeq(const std::string& seq_id) {
  SequenceManager::PreemptSeq(seq_id);
  auto seq = seq_map_[seq_id];
  if (block_manager_.IsAllocated(seq)) {
    block_manager_.Free(seq);
  }
}

void WorkerSequenceManager::OnSeqScheduled(
    SequenceScheduleMetadataPtr seq_sched_metadata) {
  ASSERT_VALID_RUNTIME(
      seq_map_.find(seq_sched_metadata->seq_id) != seq_map_.end(),
      "sequence {} not found", seq_sched_metadata->seq_id);
  ResumeSeq(seq_sched_metadata->seq_id);
  auto seq = seq_map_[seq_sched_metadata->seq_id];
  auto num_total_blocks =
      seq_sched_metadata->kvp_group_block_counter.at(kvp_group_id_);
  LOG_DEBUG("Allocating {} blocks for seq {} in group {}", num_total_blocks,
            seq->seq_id, kvp_group_id_);
  block_manager_.AllocateDelta(seq, num_total_blocks);
}

std::vector<int> WorkerSequenceManager::GetBlockTable(SequencePtr seq) const {
  return *block_manager_.GetBlockTable(seq);
}

void WorkerSequenceManager::OnAppendToken(MutableSequencePtr, std::size_t) {
  return;
}

void WorkerSequenceManager::UpdateSeqNumProcessedTokens(
    SequencePtr seq, SequenceScheduleMetadataPtr seq_sched_metadata) {
  if (kvp_group_id_ != seq_sched_metadata->kvp_group_ids.back()) return;

  if (seq_num_processed_tokens_.find(seq->seq_id) ==
      seq_num_processed_tokens_.end()) {
    seq_num_processed_tokens_[seq->seq_id] = 0;
  }

  if (!seq->GetPromptStageProcessingFinished()) {
    seq_num_processed_tokens_[seq->seq_id] += seq_sched_metadata->num_q_tokens;
    ASSERT_VALID_RUNTIME(
        seq_num_processed_tokens_[seq->seq_id] <= max_num_tokens_per_kvp_group_,
        "seq_id: {}, "
        "num_processed_tokens: {}, "
        "max_num_tokens_per_kvp_group: {}",
        seq->seq_id, seq_num_processed_tokens_[seq->seq_id],
        max_num_tokens_per_kvp_group_);
  } else {
    seq_num_processed_tokens_[seq->seq_id] += 1;
  }
}

}  // namespace vajra
