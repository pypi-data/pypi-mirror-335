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
#include <nlohmann/json.hpp>
//==============================================================================
#include "commons/StdCommon.h"
#include "native/datatypes/SequenceMetadata.h"
#include "native/datatypes/SequenceScheduleMetadata.h"
//==============================================================================
namespace vajra {
//==============================================================================
class ChromeTracer {
 public:
  ChromeTracer(std::size_t replica_id, std::string output_dir);

  // Constructor for deserialization
  ChromeTracer(std::size_t replica_id, std::string output_dir,
               const std::string& serialized_trace);

  void Put(
      const std::vector<std::shared_ptr<SequenceMetadata>>& seq_metadata_list,
      std::size_t tensor_parallel_rank, std::size_t pipeline_parallel_rank,
      std::size_t kv_parallel_rank, double start_time, double end_time);

  void PutSchedulerEvent(
      std::size_t scheduler_id,
      const std::vector<SequenceScheduleMetadata>& seq_schedule_metadata_list,
      double start_time, double end_time);

  void Merge(const ChromeTracer& other);
  void Store();

  // Pickling utility methods
  std::string GetState() const;
  std::size_t GetReplicaId() const;
  std::string GetOutputDir() const;

 private:
  const std::size_t replica_id_;
  const std::string output_dir_;
  nlohmann::json trace_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
