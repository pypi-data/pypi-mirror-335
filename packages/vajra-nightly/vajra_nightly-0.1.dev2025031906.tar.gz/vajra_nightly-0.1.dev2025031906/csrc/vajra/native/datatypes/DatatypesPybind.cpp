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
#include "native/datatypes/DatatypesPybind.h"

#include "native/datatypes/LogicalTokenBlock.h"
#include "native/datatypes/RequestOutput.h"
#include "native/datatypes/SamplerOutput.h"
#include "native/datatypes/SamplingParams.h"
#include "native/datatypes/SchedulerOutput.h"
#include "native/datatypes/Sequence.h"
#include "native/datatypes/SequenceMetadata.h"
#include "native/datatypes/SequenceScheduleMetadata.h"
#include "native/datatypes/SequenceState.h"
#include "native/datatypes/SequenceStatus.h"
//==============================================================================
void InitDatatypesPybindSubmodule(py::module_& pm) {
  auto m = pm.def_submodule("datatypes", "Datatypes submodule");

  py::class_<vajra::SequenceMetadata, std::shared_ptr<vajra::SequenceMetadata>>(
      m, "SequenceMetadata")
      .def(py::init<std::size_t, std::string, std::size_t, std::size_t,
                    std::vector<int>, std::vector<std::size_t>, bool>(),
           py::arg("schedule_id"), py::arg("seq_id"), py::arg("num_q_tokens"),
           py::arg("num_kv_tokens"), py::arg("block_table"),
           py::arg("kvp_group_ids"), py::arg("save_kv_cache"))
      .def("__str__", &vajra::SequenceMetadata::ToString)
      .def("__repr__", &vajra::SequenceMetadata::ToString)
      .def_readonly("schedule_id", &vajra::SequenceMetadata::schedule_id)
      .def_readonly("seq_id", &vajra::SequenceMetadata::seq_id)
      .def_readonly("num_q_tokens", &vajra::SequenceMetadata::num_q_tokens)
      .def_readonly("num_kv_tokens", &vajra::SequenceMetadata::num_kv_tokens)
      .def_readonly("block_table", &vajra::SequenceMetadata::block_table)
      .def_readonly("kvp_group_ids", &vajra::SequenceMetadata::kvp_group_ids)
      .def_readonly("save_kv_cache", &vajra::SequenceMetadata::save_kv_cache)
      .def_readonly("is_kvp_request", &vajra::SequenceMetadata::is_kvp_request);
  //==============================================================================
  py::class_<vajra::LogicalTokenBlock,
             std::shared_ptr<vajra::LogicalTokenBlock>>(m, "LogicalTokenBlock")
      .def(py::init<std::size_t, std::size_t>(), py::arg("block_number"),
           py::arg("block_size"))
      .def_readonly("block_number", &vajra::LogicalTokenBlock::block_number)
      .def_readonly("block_size", &vajra::LogicalTokenBlock::block_size)
      .def_property_readonly("token_ids",
                             &vajra::LogicalTokenBlock::GetTokenIds)
      .def_property_readonly("num_tokens",
                             &vajra::LogicalTokenBlock::GetNumTokens)
      .def_property_readonly("is_empty", &vajra::LogicalTokenBlock::IsEmpty)
      .def_property_readonly("num_empty_slots",
                             &vajra::LogicalTokenBlock::NumEmptySlots)
      .def_property_readonly("is_full", &vajra::LogicalTokenBlock::IsFull)
      .def("append_tokens", &vajra::LogicalTokenBlock::AppendTokens)
      .def("get_last_token_id", &vajra::LogicalTokenBlock::GetLastTokenId)
      .def(py::pickle(
          [](const vajra::LogicalTokenBlock& p) {  // __getstate__
            return py::make_tuple(p.block_number, p.block_size,
                                  p.GetTokenIdsCopy(), p.GetNumTokens());
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(
                t.size() == 4, "Invalid pickled state for LogicalTokenBlock!");

            return vajra::LogicalTokenBlock(
                t[0].cast<std::size_t>(), t[1].cast<std::size_t>(),
                t[2].cast<std::vector<std::size_t>>(),
                t[3].cast<std::size_t>());
          }));
  //==============================================================================
  py::class_<vajra::SamplerOutput, std::shared_ptr<vajra::SamplerOutput>>(
      m, "SamplerOutput")
      .def(py::init<std::size_t, std::string, std::vector<std::size_t>>(),
           py::arg("schedule_id"), py::arg("seq_id"), py::arg("output_tokens"))
      .def("__str__", &vajra::SamplerOutput::ToString)
      .def("__repr__", &vajra::SamplerOutput::ToString)
      .def_property_readonly("schedule_id",
                             &vajra::SamplerOutput::GetScheduleId)
      .def_property_readonly("seq_id", &vajra::SamplerOutput::GetSeqId)
      .def_property_readonly("output_tokens",
                             &vajra::SamplerOutput::GetOutputTokens)
      .def(py::pickle(
          [](const vajra::SamplerOutput& p) {  // __getstate__
            return py::make_tuple(p.GetScheduleId(), p.GetSeqIdCopy(),
                                  p.GetOutputTokensCopy());
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(t.size() == 3,
                                 "Invalid pickled state for SamplerOutput!");

            return vajra::SamplerOutput(t[0].cast<std::size_t>(),
                                        t[1].cast<std::string>(),
                                        t[2].cast<std::vector<std::size_t>>());
          }));
  //==============================================================================
  py::enum_<vajra::SequenceStatus>(m, "SequenceStatus")
      .value("WAITING", vajra::SequenceStatus::Waiting)
      .value("WAITING_PREEMPTED", vajra::SequenceStatus::WaitingPreempted)
      .value("RUNNING", vajra::SequenceStatus::Running)
      .value("PAUSED", vajra::SequenceStatus::Paused)
      .value("FINISHED_STOPPED", vajra::SequenceStatus::FinishedStopped)
      .value("FINISHED_LENGTH_CAPPED",
             vajra::SequenceStatus::FinishedLengthCapped)
      .value("FINISHED_IGNORED", vajra::SequenceStatus::FinishedIgnored)
      .def_static("is_finished", &vajra::sequence_status::IsFinished)
      .def_static("is_executing", &vajra::sequence_status::IsExecuting)
      .def_static("is_waiting", &vajra::sequence_status::IsWaiting)
      .def_static("is_waiting_preempted",
                  &vajra::sequence_status::IsWaitingPreempted)
      .def_static("is_paused", &vajra::sequence_status::IsPaused)
      .def_static("is_running", &vajra::sequence_status::IsRunning)
      .def_static("get_finished_reason",
                  &vajra::sequence_status::GetFinishedReason);
  //==============================================================================
  py::enum_<vajra::SamplingType>(m, "SamplingType")
      .value("GREEDY", vajra::SamplingType::Greedy)
      .value("RANDOM", vajra::SamplingType::Random);
  //==============================================================================
  py::class_<vajra::SamplingParams>(m, "SamplingParams")
      .def(py::init<float, float, int, bool, std::size_t>(),
           py::arg("temperature") = 1.0f, py::arg("top_p") = 1.0f,
           py::arg("top_k") = -1, py::arg("ignore_eos") = false,
           py::arg("max_tokens") = 2048)
      .def("__str__", &vajra::SamplingParams::ToString)
      .def("__repr__", &vajra::SamplingParams::ToString)
      .def_readonly("temperature", &vajra::SamplingParams::temperature)
      .def_readonly("top_p", &vajra::SamplingParams::top_p)
      .def_readonly("top_k", &vajra::SamplingParams::top_k)
      .def_readonly("ignore_eos", &vajra::SamplingParams::ignore_eos)
      .def_readonly("max_tokens", &vajra::SamplingParams::max_tokens)
      .def_property_readonly("sampling_type",
                             &vajra::SamplingParams::GetSamplingType)
      .def(py::pickle(
          [](const vajra::SamplingParams& p) {  // __getstate__
            return py::make_tuple(p.temperature, p.top_p, p.top_k, p.ignore_eos,
                                  p.max_tokens);
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(t.size() == 5,
                                 "Invalid pickled state for SamplingParams!");

            return vajra::SamplingParams(
                t[0].cast<double>(), t[1].cast<double>(), t[2].cast<int>(),
                t[3].cast<bool>(), t[4].cast<std::size_t>());
          }));
  //==============================================================================
  py::class_<vajra::SequenceState>(m, "SequenceState")
      .def(py::init<std::string, double, std::size_t>(), py::arg("id"),
           py::arg("arrived_at"), py::arg("num_prompt_tokens"))
      .def_property_readonly("id", &vajra::SequenceState::GetId)
      .def_property_readonly("arrived_at", &vajra::SequenceState::GetArrivedAt)
      .def_property_readonly("num_prompt_tokens",
                             &vajra::SequenceState::GetNumPromptTokens)
      .def_property_readonly("num_output_tokens",
                             &vajra::SequenceState::GetNumOutputTokens)
      .def_property_readonly("num_total_tokens",
                             &vajra::SequenceState::GetNumTotalTokens)
      .def_property("status", &vajra::SequenceState::GetStatus,
                    &vajra::SequenceState::SetStatus)
      .def_property_readonly("is_scheduled",
                             &vajra::SequenceState::GetIsScheduled)
      .def_property_readonly("is_completed",
                             &vajra::SequenceState::GetIsCompleted)
      .def_property_readonly("scheduled_at",
                             &vajra::SequenceState::GetScheduledAt)
      .def_property_readonly("completed_at",
                             &vajra::SequenceState::GetCompletedAt)
      .def_property_readonly(
          "prompt_processing_completed_at",
          &vajra::SequenceState::GetPromptProcessingCompletedAt)
      .def_property_readonly("e2e_time", &vajra::SequenceState::GetE2ETime)
      .def_property_readonly(
          "e2e_time_piecewise_normalized",
          &vajra::SequenceState::GetE2ETimePiecewiseNormalized)
      .def_property_readonly("e2e_time_normalized",
                             &vajra::SequenceState::GetE2ETimeNormalized)
      .def_property_readonly("e2e_prefill_time",
                             &vajra::SequenceState::GetE2EPrefillTime)
      .def_property_readonly("e2e_prefill_time_normalized",
                             &vajra::SequenceState::GetE2EPrefillTimeNormalized)
      .def_property_readonly(
          "e2e_prefill_time_piecewise_normalized",
          &vajra::SequenceState::GetE2EPrefillTimePiecewiseNormalized)
      .def_property_readonly(
          "prefill_execution_plus_preemption_time",
          &vajra::SequenceState::GetPrefillExecutionPlusPreemptionTime)
      .def_property_readonly(
          "decode_execution_plus_preemption_time",
          &vajra::SequenceState::GetDecodeExecutionPlusPreemptionTime)
      .def_property_readonly(
          "prefill_execution_plus_preemption_time_normalized",
          &vajra::SequenceState::
              GetPrefillExecutionPlusPreemptionTimeNormalized)
      .def_property_readonly(
          "decode_execution_plus_preemption_time_normalized",
          &vajra::SequenceState::GetDecodeExecutionPlusPreemptionTimeNormalized)
      .def_property_readonly("scheduling_delay",
                             &vajra::SequenceState::GetSchedulingDelay)
      .def_property_readonly("execution_time",
                             &vajra::SequenceState::GetExecutionTime)
      .def_property_readonly("execution_time_normalized",
                             &vajra::SequenceState::GetExecutionTimeNormalized)
      .def_property_readonly("preempted_time",
                             &vajra::SequenceState::GetPreemptedTime)
      .def_property_readonly(
          "execution_plus_preemption_time",
          &vajra::SequenceState::GetExecutionPlusPreemptionTime)
      .def_property_readonly(
          "execution_plus_preemption_time_normalized",
          &vajra::SequenceState::GetExecutionPlusPreemptionTimeNormalized)
      .def_property_readonly("last_token_generation_time",
                             &vajra::SequenceState::GetLastTokenGenerationTime)
      .def_property_readonly("num_restarts",
                             &vajra::SequenceState::GetNumRestarts)
      .def_property_readonly("num_pauses", &vajra::SequenceState::GetNumPauses)
      .def_property_readonly("is_ignore_finished",
                             &vajra::SequenceState::GetIsIgnoreFinished)
      .def("on_prompt_processing_completed",
           &vajra::SequenceState::OnPromptProcessingCompleted)
      .def("on_token_generated", &vajra::SequenceState::OnTokenGenerated);
  //==============================================================================
  py::class_<vajra::SequenceParams>(m, "SequenceParams")
      .def(py::init<std::string, std::string, std::vector<vajra::TokenId>,
                    std::size_t, vajra::TokenId, double,
                    vajra::SamplingParams>(),
           py::arg("seq_id"), py::arg("prompt"), py::arg("prompt_token_ids"),
           py::arg("block_size"), py::arg("eos_token_id"),
           py::arg("arrival_time"), py::arg("sampling_params"))
      .def_readonly("seq_id", &vajra::SequenceParams::seq_id)
      .def_readonly("prompt", &vajra::SequenceParams::prompt)
      .def_readonly("prompt_token_ids",
                    &vajra::SequenceParams::prompt_token_ids)
      .def_readonly("block_size", &vajra::SequenceParams::block_size)
      .def_readonly("eos_token_id", &vajra::SequenceParams::eos_token_id)
      .def_readonly("arrival_time", &vajra::SequenceParams::arrival_time)
      .def_readonly("sampling_params", &vajra::SequenceParams::sampling_params)
      .def(py::pickle(
          [](const vajra::SequenceParams& p) {  // __getstate__
            return py::make_tuple(p.seq_id, p.prompt, p.prompt_token_ids,
                                  p.block_size, p.eos_token_id, p.arrival_time,
                                  p.sampling_params);
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(t.size() == 7,
                                 "Invalid pickled state for SequenceParams!");
            return vajra::SequenceParams(
                t[0].cast<std::string>(), t[1].cast<std::string>(),
                t[2].cast<std::vector<vajra::TokenId>>(),
                t[3].cast<std::size_t>(), t[4].cast<vajra::TokenId>(),
                t[5].cast<double>(), t[6].cast<vajra::SamplingParams>());
          }));
  //==============================================================================
  py::class_<vajra::Sequence, std::shared_ptr<vajra::Sequence>>(m, "Sequence")
      .def(py::init<std::string, std::string, std::vector<vajra::TokenId>,
                    std::size_t, vajra::TokenId, double,
                    vajra::SamplingParams>(),
           py::arg("seq_id"), py::arg("prompt"), py::arg("prompt_token_ids"),
           py::arg("block_size"), py::arg("eos_token_id"),
           py::arg("arrival_time"), py::arg("sampling_params"))
      .def(py::init<vajra::SequenceParams&>(), py::arg("params"))
      .def_readonly("seq_id", &vajra::Sequence::seq_id)
      .def_readonly("prompt", &vajra::Sequence::prompt)
      .def_readonly("block_size", &vajra::Sequence::block_size)
      .def_readonly("eos_token_id", &vajra::Sequence::eos_token_id)
      .def_readonly("arrival_time", &vajra::Sequence::arrival_time)
      .def_readonly("sampling_params", &vajra::Sequence::sampling_params)
      .def_readwrite("output_text", &vajra::Sequence::output_text)
      .def_property("tokens", &vajra::Sequence::GetTokens,
                    &vajra::Sequence::SetTokens)
      .def("append_tokens", &vajra::Sequence::ExtendTokens)
      .def_readwrite("prefix_offset", &vajra::Sequence::prefix_offset)
      .def_readwrite("read_offset", &vajra::Sequence::read_offset)
      .def_property_readonly("prompt_token_ids",
                             &vajra::Sequence::GetPromptTokenIds)
      .def_property_readonly("output_token_ids",
                             &vajra::Sequence::GetOutputTokenIds)
      .def_property_readonly("prompt_processing_finished",
                             &vajra::Sequence::GetPromptProcessingFinished)
      .def_property_readonly("prompt_stage_processing_finished",
                             &vajra::Sequence::GetPromptStageProcessingFinished)
      .def_property_readonly("logical_token_blocks",
                             &vajra::Sequence::GetLogicalTokenBlocks)
      .def_property_readonly("state", &vajra::Sequence::GetState)
      .def_property("status", &vajra::Sequence::GetStatus,
                    &vajra::Sequence::SetStatus)
      .def("update_prompt_tokens_processed",
           &vajra::Sequence::UpdatePromptTokensProcessed)
      .def("update_prompt_tokens_stage_processed",
           &vajra::Sequence::UpdatePromptTokensStageProcessed)
      .def("append_token_id", &vajra::Sequence::AppendTokenId)
      .def("__len__", &vajra::Sequence::Length)
      .def_property_readonly("prompt_len", &vajra::Sequence::GetPromptLength)
      .def_property_readonly("output_len", &vajra::Sequence::GetOutputLength)
      .def("get_num_prompt_tokens_processed",
           &vajra::Sequence::GetNumPromptTokensProcessed)
      .def("get_num_prompt_tokens_stage_processed",
           &vajra::Sequence::GetNumPromptTokensStageProcessed)
      .def("get_num_tokens_stage_processed",
           &vajra::Sequence::GetNumTokensStageProcessed)
      .def("get_num_tokens_processed", &vajra::Sequence::GetNumTokensProcessed)
      .def("get_last_token_id", &vajra::Sequence::GetLastTokenId)
      .def("get_last_n_token_ids", &vajra::Sequence::GetLastNTokenIds,
           py::arg("n"), py::arg("truncate") = false)
      .def("is_finished", &vajra::Sequence::IsFinished)
      .def("is_waiting", &vajra::Sequence::IsWaiting)
      .def("is_paused", &vajra::Sequence::IsPaused)
      .def("is_running", &vajra::Sequence::IsRunning)
      .def("is_waiting_preempted", &vajra::Sequence::IsWaitingPreempted)
      .def("reset", &vajra::Sequence::Reset)
      .def("check_stop", &vajra::Sequence::CheckStop)
      .def("__str__", &vajra::Sequence::ToString)
      .def("__repr__", &vajra::Sequence::ToString);
  //==============================================================================
  py::class_<vajra::SequenceScheduleMetadata,
             std::shared_ptr<vajra::SequenceScheduleMetadata>>(
      m, "SequenceScheduleMetadata")
      .def(py::init<std::size_t, std::string, std::size_t,
                    std::unordered_map<std::size_t, std::size_t>,
                    std::vector<std::size_t>>(),
           py::arg("schedule_id"), py::arg("seq_id"), py::arg("num_q_tokens"),
           py::arg("kvp_group_block_counter"), py::arg("kvp_group_ids"))
      .def_readonly("schedule_id",
                    &vajra::SequenceScheduleMetadata::schedule_id)
      .def_readonly("seq_id", &vajra::SequenceScheduleMetadata::seq_id)
      .def_readonly("num_q_tokens",
                    &vajra::SequenceScheduleMetadata::num_q_tokens)
      .def_readonly("kvp_group_block_counter",
                    &vajra::SequenceScheduleMetadata::kvp_group_block_counter)
      .def_readonly("kvp_group_ids",
                    &vajra::SequenceScheduleMetadata::kvp_group_ids)
      .def_readonly("is_kvp_request",
                    &vajra::SequenceScheduleMetadata::is_kvp_request)
      .def(py::pickle(
          [](const vajra::SequenceScheduleMetadata& p) {
            return py::make_tuple(p.schedule_id, p.seq_id, p.num_q_tokens,
                                  p.kvp_group_block_counter, p.kvp_group_ids);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(
                t.size() == 5,
                "Invalid pickled state for SequenceScheduleMetadata");
            return vajra::SequenceScheduleMetadata(
                t[0].cast<std::size_t>(), t[1].cast<std::string>(),
                t[2].cast<std::size_t>(),
                t[3].cast<std::unordered_map<std::size_t, std::size_t>>(),
                t[4].cast<std::vector<std::size_t>>());
          }));
  //==============================================================================
  py::class_<vajra::SchedulerOutput, std::shared_ptr<vajra::SchedulerOutput>>(
      m, "SchedulerOutput")
      .def(py::init<std::size_t, std::vector<std::string>,
                    std::vector<std::string>,
                    std::vector<vajra::SequenceScheduleMetadataPtr>>(),
           py::arg("id"), py::arg("ignored_seq_ids"),
           py::arg("preempted_seq_ids"), py::arg("seq_schedule_metadata_list"))
      .def_readonly("id", &vajra::SchedulerOutput::id)
      .def_readonly("ignored_seq_ids", &vajra::SchedulerOutput::ignored_seq_ids)
      .def_readonly("preempted_seq_ids",
                    &vajra::SchedulerOutput::preempted_seq_ids)
      .def_readonly("seq_schedule_metadata_list",
                    &vajra::SchedulerOutput::seq_schedule_metadata_list)
      .def_readonly("is_empty", &vajra::SchedulerOutput::is_empty)
      .def_readonly("has_no_output", &vajra::SchedulerOutput::has_no_output)
      .def(py::pickle(
          [](const vajra::SchedulerOutput& p) {
            return py::make_tuple(p.id, p.ignored_seq_ids, p.preempted_seq_ids,
                                  p.seq_schedule_metadata_list);
          },
          [](py::tuple t) {
            ASSERT_VALID_RUNTIME(t.size() == 4,
                                 "Invalid pickled state for SchedulerOutput");
            return vajra::SchedulerOutput(
                t[0].cast<std::size_t>(), t[1].cast<std::vector<std::string>>(),
                t[2].cast<std::vector<std::string>>(),
                t[3].cast<std::vector<vajra::SequenceScheduleMetadataPtr>>());
          }));
  //==============================================================================
  py::class_<vajra::RequestOutput>(m, "RequestOutput")
      .def(py::init<std::shared_ptr<vajra::Sequence>>(), py::arg("seq"))
      .def_readonly("seq", &vajra::RequestOutput::seq)
      .def_readonly("finished", &vajra::RequestOutput::finished)
      .def_readonly("finish_reason", &vajra::RequestOutput::finish_reason)
      .def_property_readonly("text", &vajra::RequestOutput::GetText)
      .def_property_readonly("seq_id", &vajra::RequestOutput::GetSeqId)
      .def_property_readonly("prompt", &vajra::RequestOutput::GetPrompt)
      .def_property_readonly("prompt_token_ids",
                             &vajra::RequestOutput::GetPromptTokenIds)
      .def_property_readonly("token_ids", &vajra::RequestOutput::GetTokenIds);
  //==============================================================================
  py::class_<vajra::SequenceWithPriority>(m, "SequenceWithPriority")
      .def(py::init<std::pair<double, double>,
                    std::shared_ptr<vajra::Sequence>>(),
           py::arg("priority"), py::arg("seq"))
      .def(
          "__lt__",
          [](const vajra::SequenceWithPriority& self,
             const vajra::SequenceWithPriority& other) { return self < other; })
      .def_property_readonly("priority",
                             &vajra::SequenceWithPriority::GetPriority)
      .def_property_readonly("seq", &vajra::SequenceWithPriority::GetSequence);
  //==============================================================================
}
//==============================================================================
