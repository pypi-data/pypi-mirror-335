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

#include "native/scheduler/SchedulerPybind.h"

#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// clang-format off
// Include vidur headers
#include "vidur/execution_time_predictor/execution_time_predictor.h"
// clang-format on

#include "native/configs/CacheConfig.h"
#include "native/configs/ModelConfig.h"
#include "native/configs/ParallelConfig.h"
#include "native/scheduler/replica_schedulers/trackers/BatchFormationTracker.h"
#include "native/scheduler/replica_schedulers/trackers/BatchFormationTrackerWithRuntimePrediction.h"
#include "native/scheduler/replica_schedulers/trackers/KvpBatchTracker.h"
#include "native/scheduler/replica_schedulers/trackers/KvpStateTracker.h"

namespace py = pybind11;

void InitKvpBatchTrackerPybind(py::module& m) {
  py::class_<vajra::KvpBatchTracker>(m, "KvpBatchTracker")
      .def(py::init<std::size_t>())
      .def("add_sequence", &vajra::KvpBatchTracker::AddSequence, py::arg("seq"),
           py::arg("num_q_tokens"), py::arg("active_kvp_group_ids"),
           py::arg("kv_token_info"), py::arg("num_processed_tokens"))
      .def("_get_q_tokens_for_kvp_groups",
           &vajra::KvpBatchTracker::GetQTokensForKvpGroups,
           py::arg("active_kvp_group_ids"))
      .def("get_free_kvp_groups", &vajra::KvpBatchTracker::GetFreeKvpGroups,
           py::arg("token_threshold") = vajra::ALLOCATION_MAX_TOKEN_THRESHOLD)
      .def("get_per_group_sequences",
           &vajra::KvpBatchTracker::GetPerGroupSequences,
           py::arg("kvp_group_id"))
      .def("get_per_group_q_tokens",
           &vajra::KvpBatchTracker::GetPerGroupQTokens, py::arg("kvp_group_id"))
      .def("get_per_group_kv_tokens",
           &vajra::KvpBatchTracker::GetPerGroupKvTokens,
           py::arg("kvp_group_id"))
      .def("get_per_group_active_kvp_groups",
           &vajra::KvpBatchTracker::GetPerGroupActiveKvpGroups,
           py::arg("kvp_group_id"))
      .def("get_per_group_last_kvp_group_ids",
           &vajra::KvpBatchTracker::GetPerGroupLastKvpGroupIds,
           py::arg("kvp_group_id"));
}

void InitKvpStateTrackerPybind(py::module& m) {
  py::class_<vajra::KvpStateTracker, std::shared_ptr<vajra::KvpStateTracker>>(
      m, "KvpStateTracker")
      .def(py::init<const vajra::ModelConfig&, const vajra::CacheConfig&,
                    const vajra::ParallelConfig&>(),
           py::arg("model_config"), py::arg("cache_config"),
           py::arg("parallel_config"))
      .def("start_batch_formation",
           &vajra::KvpStateTracker::StartBatchFormation)
      .def("get_batch_tracker_q_tokens",
           &vajra::KvpStateTracker::GetBatchTrackerQTokens, py::arg("seq"))
      .def("get_batch_tracker_free_groups",
           &vajra::KvpStateTracker::GetBatchTrackerFreeGroups)
      .def("add_sequence_to_batch", &vajra::KvpStateTracker::AddSequenceToBatch,
           py::arg("seq"), py::arg("num_q_tokens"),
           py::arg("active_kvp_group_ids"))
      .def("get_batch_tracker_per_group_info",
           &vajra::KvpStateTracker::GetBatchTrackerPerGroupInfo,
           py::arg("kvp_group_id"))
      .def("get_max_seq_len", &vajra::KvpStateTracker::GetMaxSeqLen)
      .def("get_allocation_order", &vajra::KvpStateTracker::GetAllocationOrder,
           py::arg("kvp_group_ids"))
      .def("allocate", &vajra::KvpStateTracker::Allocate, py::arg("seq"))
      .def("free_seq", &vajra::KvpStateTracker::FreeSeq, py::arg("seq"))
      .def("get_last_kv_group_id", &vajra::KvpStateTracker::GetLastKvGroupId,
           py::arg("seq"))
      .def("can_append_slot", &vajra::KvpStateTracker::CanAppendSlot,
           py::arg("seq"))
      .def("append_slot", &vajra::KvpStateTracker::AppendSlot, py::arg("seq"),
           py::arg("num_total_blocks"))
      .def("get_active_kvp_group_ids",
           &vajra::KvpStateTracker::GetActiveKvpGroupIds, py::arg("seq"))
      .def("update_prefill_work", &vajra::KvpStateTracker::UpdatePrefillWork,
           py::arg("seq"), py::arg("current_tokens"), py::arg("new_tokens"))
      .def("get_kvp_group_block_counter",
           &vajra::KvpStateTracker::GetKvpGroupBlockCounter, py::arg("seq_id"))
      .def("get_sequence_kv_token_info",
           &vajra::KvpStateTracker::GetSequenceKvTokenInfo, py::arg("seq"),
           py::arg("active_kvp_group_ids"))
      .def("get_max_num_tokens_per_kvp_group",
           &vajra::KvpStateTracker::GetMaxNumTokensPerKvpGroup)
      .def("get_kvp_size", &vajra::KvpStateTracker::GetKvpSize);
}

void InitBatchFormationTrackerPybind(py::module& m) {
  py::class_<vajra::BatchFormationTracker,
             std::shared_ptr<vajra::BatchFormationTracker>>(
      m, "BatchFormationTracker")
      .def(py::init<const std::size_t, const std::size_t,
                    std::shared_ptr<vajra::KvpStateTracker>>(),
           py::arg("schedule_id"), py::arg("max_micro_batch_size"),
           py::arg("kvp_state_tracker"))
      .def("add_sequence", &vajra::BatchFormationTracker::AddSequence,
           py::arg("seq"), py::arg("num_q_tokens"))
      .def("add_ignored_sequence",
           &vajra::BatchFormationTracker::AddIgnoredSequence, py::arg("seq"))
      .def("add_preempted_sequence",
           &vajra::BatchFormationTracker::AddPreemptedSequence, py::arg("seq"))
      .def("can_add_sequences", &vajra::BatchFormationTracker::CanAddSequences)
      .def("get_batch", &vajra::BatchFormationTracker::GetBatch);
}

void InitBatchFormationTrackerWithRuntimePredictionPybind(py::module& m) {
  py::class_<
      vajra::BatchFormationTrackerWithRuntimePrediction,
      vajra::BatchFormationTracker,
      std::shared_ptr<vajra::BatchFormationTrackerWithRuntimePrediction>>(
      m, "BatchFormationTrackerWithRuntimePrediction")
      .def(
          py::init([](const std::size_t schedule_id,
                      const std::size_t max_micro_batch_size,
                      const std::size_t pipeline_parallel_size,
                      std::shared_ptr<vajra::KvpStateTracker> kvp_state_tracker,
                      const std::size_t max_chunk_size,
                      const std::size_t min_chunk_size,
                      py::capsule predictor_capsule) {
            // Check capsule name
            if (!predictor_capsule || std::string(predictor_capsule.name()) !=
                                          "ExecutionTimePredictorPtr") {
              throw std::runtime_error(
                  "Invalid or missing ExecutionTimePredictor capsule.");
            }

            // Retrieve pointer to the std::shared_ptr
            auto* sp_predictor_ptr = static_cast<std::shared_ptr<
                vidur::execution_time_predictor::ExecutionTimePredictor>*>(
                predictor_capsule.get_pointer());

            if (!sp_predictor_ptr) {
              throw std::runtime_error(
                  "Capsule contained a null predictor pointer.");
            }

            // Copy the shared_ptr so we have local ownership
            auto predictor_shared = *sp_predictor_ptr;
            if (!predictor_shared) {
              throw std::runtime_error(
                  "Shared predictor is null inside the capsule.");
            }

            // Create the object with the C++ predictor reference
            return std::make_shared<
                vajra::BatchFormationTrackerWithRuntimePrediction>(
                schedule_id, max_micro_batch_size, pipeline_parallel_size,
                kvp_state_tracker, max_chunk_size, min_chunk_size,
                predictor_shared);
          }),
          py::arg("schedule_id"), py::arg("max_micro_batch_size"),
          py::arg("pipeline_parallel_size"), py::arg("kvp_state_tracker"),
          py::arg("max_chunk_size"), py::arg("min_chunk_size"),
          py::arg("execution_time_predictor_capsule"))
      .def("add_sequence",
           &vajra::BatchFormationTrackerWithRuntimePrediction::AddSequence,
           py::arg("seq"), py::arg("num_q_tokens"))
      .def("get_batch_execution_time",
           &vajra::BatchFormationTrackerWithRuntimePrediction::
               GetBatchExecutionTime,
           py::arg("kvp_group_id"))
      .def("get_batch_execution_time_for_kvp_groups",
           &vajra::BatchFormationTrackerWithRuntimePrediction::
               GetBatchExecutionTimeForKvpGroups,
           py::arg("kvp_group_ids"))
      .def("get_max_chunk_size_for_seq",
           &vajra::BatchFormationTrackerWithRuntimePrediction::
               GetMaxChunkSizeForSeq,
           py::arg("seq"), py::arg("active_kvp_group_ids"),
           py::arg("target_batch_time"));
}

void InitSchedulerPybindSubmodule(py::module& m) {
  auto scheduler_module = m.def_submodule("scheduler");
  InitKvpBatchTrackerPybind(scheduler_module);
  InitKvpStateTrackerPybind(scheduler_module);
  InitBatchFormationTrackerPybind(scheduler_module);
  InitBatchFormationTrackerWithRuntimePredictionPybind(scheduler_module);
}
