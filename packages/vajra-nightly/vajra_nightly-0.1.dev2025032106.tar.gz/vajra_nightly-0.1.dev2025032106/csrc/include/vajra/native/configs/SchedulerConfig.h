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
//==============================================================================
namespace vajra {
//==============================================================================
enum class SchedulerType { FCFS, FCFS_FIXED_CHUNK, EDF, LRS, ST };

class BaseReplicaSchedulerConfig {
 public:
  explicit BaseReplicaSchedulerConfig(std::size_t max_batch_size_param = 128)
      : max_batch_size(max_batch_size_param) {}

  ~BaseReplicaSchedulerConfig() = default;
  virtual std::size_t get_max_num_batched_tokens() const {
    return max_batch_size;
  }

  const std::size_t max_batch_size;
};

//==============================================================================
class FcfsFixedChunkReplicaSchedulerConfig : public BaseReplicaSchedulerConfig {
 public:
  FcfsFixedChunkReplicaSchedulerConfig(std::size_t max_batch_size_param = 128,
                                       std::size_t chunk_size_param = 2048)
      : BaseReplicaSchedulerConfig(max_batch_size_param),
        chunk_size(chunk_size_param) {}

  std::size_t get_max_num_batched_tokens() { return chunk_size; }

  static SchedulerType get_type() { return SchedulerType::FCFS_FIXED_CHUNK; }

  const std::size_t chunk_size;
};

//==============================================================================
struct FcfsReplicaSchedulerConfig : public BaseReplicaSchedulerConfig {
  FcfsReplicaSchedulerConfig(std::size_t max_batch_size_param = 128,
                             std::size_t max_chunk_size_param = 8192,
                             std::size_t min_chunk_size_param = 32,
                             float target_batch_time_param = 0.05)
      : BaseReplicaSchedulerConfig(max_batch_size_param),
        max_chunk_size(max_chunk_size_param),
        min_chunk_size(min_chunk_size_param),
        target_batch_time(target_batch_time_param) {}

  std::size_t get_max_num_batched_tokens() const { return max_chunk_size; }

  static SchedulerType get_type() { return SchedulerType::FCFS; }

  const std::size_t max_chunk_size;
  const std::size_t min_chunk_size;
  const float target_batch_time;
};

//==============================================================================
class EdfReplicaSchedulerConfig : public BaseReplicaSchedulerConfig {
 public:
  EdfReplicaSchedulerConfig(std::size_t max_batch_size_param = 128,
                            std::size_t max_chunk_size_param = 8192,
                            std::size_t min_chunk_size_param = 32,
                            float target_batch_time_param = 0.05,
                            float deadline_multiplier_param = 1.5,
                            float min_deadline_param = 0.5)
      : BaseReplicaSchedulerConfig(max_batch_size_param),
        max_chunk_size(max_chunk_size_param),
        min_chunk_size(min_chunk_size_param),
        target_batch_time(target_batch_time_param),
        deadline_multiplier(deadline_multiplier_param),
        min_deadline(min_deadline_param) {}

  std::size_t get_max_num_batched_tokens() { return max_chunk_size; }

  static SchedulerType get_type() { return SchedulerType::EDF; }

  const std::size_t max_chunk_size;
  const std::size_t min_chunk_size;
  const float target_batch_time;
  const float deadline_multiplier;
  const float min_deadline;
};

//==============================================================================
class LrsReplicaSchedulerConfig : public BaseReplicaSchedulerConfig {
 public:
  LrsReplicaSchedulerConfig(std::size_t max_batch_size_param = 128,
                            std::size_t max_chunk_size_param = 8192,
                            std::size_t min_chunk_size_param = 32,
                            float target_batch_time_param = 0.05,
                            float deadline_multiplier_param = 1.5,
                            float min_deadline_param = 0.5)
      : BaseReplicaSchedulerConfig(max_batch_size_param),
        max_chunk_size(max_chunk_size_param),
        min_chunk_size(min_chunk_size_param),
        target_batch_time(target_batch_time_param),
        deadline_multiplier(deadline_multiplier_param),
        min_deadline(min_deadline_param) {}

  std::size_t get_max_num_batched_tokens() { return max_chunk_size; }

  static SchedulerType get_type() { return SchedulerType::LRS; }

  const std::size_t max_chunk_size;
  const std::size_t min_chunk_size;
  const float target_batch_time;
  const float deadline_multiplier;
  const float min_deadline;
};

//==============================================================================
class StReplicaSchedulerConfig : public BaseReplicaSchedulerConfig {
 public:
  StReplicaSchedulerConfig(
      std::size_t max_batch_size_param = 128,
      std::size_t max_chunk_size_param = 8192,
      std::size_t min_chunk_size_param = 32,
      float target_batch_time_param = 0.05,
      float deadline_multiplier_param = 1.5, float min_deadline_param = 0.5,
      std::size_t long_seq_kv_cache_len_threshold_param = 256 * 1024)
      : BaseReplicaSchedulerConfig(max_batch_size_param),
        max_chunk_size(max_chunk_size_param),
        min_chunk_size(min_chunk_size_param),
        target_batch_time(target_batch_time_param),
        deadline_multiplier(deadline_multiplier_param),
        min_deadline(min_deadline_param),
        long_seq_kv_cache_len_threshold(long_seq_kv_cache_len_threshold_param) {
  }

  std::size_t get_max_num_batched_tokens() { return max_chunk_size; }

  static SchedulerType get_type() { return SchedulerType::ST; }

  const std::size_t max_chunk_size;
  const std::size_t min_chunk_size;
  const float target_batch_time;
  const float deadline_multiplier;
  const float min_deadline;
  const std::size_t long_seq_kv_cache_len_threshold;
};
//==============================================================================
enum class ReplicasetSchedulerType { PULL, ROUND_ROBIN };

//==============================================================================
struct BaseReplicasetSchedulerConfig {
  virtual ~BaseReplicasetSchedulerConfig() = default;
};

//==============================================================================
struct PullReplicasetSchedulerConfig : public BaseReplicasetSchedulerConfig {
  static ReplicasetSchedulerType get_type() {
    return ReplicasetSchedulerType::PULL;
  }
};

//==============================================================================
struct RoundRobinReplicasetSchedulerConfig
    : public BaseReplicasetSchedulerConfig {
  static ReplicasetSchedulerType get_type() {
    return ReplicasetSchedulerType::ROUND_ROBIN;
  }
};
//==============================================================================
}  // namespace vajra
//==============================================================================
