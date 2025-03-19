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
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "native/core/BlockSpaceManager.h"
#include "native/core/EngineSequenceManager.h"
#include "native/core/Tokenizer.h"
#include "native/core/WorkerSequenceManager.h"

namespace py = pybind11;

void InitCorePybindSubmodule(py::module& pm) {
  auto m = pm.def_submodule("core", "Core submodule");

  py::class_<vajra::BlockSpaceManager,
             std::shared_ptr<vajra::BlockSpaceManager>>(m, "BlockSpaceManager")
      .def(py::init<int, int, int, float>(), py::arg("block_size"),
           py::arg("num_gpu_blocks"), py::arg("max_model_len"),
           py::arg("watermark") = 0.01f)
      .def("can_allocate_blocks", &vajra::BlockSpaceManager::CanAllocateBlocks)
      .def("allocate", &vajra::BlockSpaceManager::Allocate)
      .def("allocate_delta", &vajra::BlockSpaceManager::AllocateDelta)
      .def("can_append_slot", &vajra::BlockSpaceManager::CanAppendSlot)
      .def("append_slot", &vajra::BlockSpaceManager::AppendSlot)
      .def("free", &vajra::BlockSpaceManager::Free)
      .def("get_block_table", &vajra::BlockSpaceManager::GetBlockTableCopy)
      .def("is_allocated", &vajra::BlockSpaceManager::IsAllocated);

  py::class_<vajra::Tokenizer, std::shared_ptr<vajra::Tokenizer>>(m,
                                                                  "Tokenizer")
      .def_static("from_path", &vajra::Tokenizer::FromPath)
      .def("encode", &vajra::Tokenizer::Encode)
      .def("decode", &vajra::Tokenizer::Decode)
      .def("partial_decode", &vajra::Tokenizer::PartialDecode);

  py::class_<vajra::SequenceManager, vajra::PySequenceManager,
             std::shared_ptr<vajra::SequenceManager>>(m, "SequenceManager")
      .def(py::init<bool>())
      .def("add_seq", &vajra::SequenceManager::AddSeq)
      .def("get_seq", &vajra::SequenceManager::GetSeq)
      .def("on_schedule", &vajra::SequenceManager::OnSchedule)
      .def("on_step_completed", &vajra::SequenceManager::OnStepCompleted)
      .def("on_stage_completed", &vajra::SequenceManager::OnStageCompleted)
      .def("generate_request_outputs",
           &vajra::SequenceManager::GenerateRequestOutputs);

  py::class_<vajra::EngineSequenceManager, vajra::SequenceManager,
             std::shared_ptr<vajra::EngineSequenceManager>>(
      m, "EngineSequenceManager")
      .def(py::init<std::shared_ptr<vajra::Tokenizer>, bool>(),
           py::arg("tokenizer"), py::arg("enable_sequence_pipeline_parallel"));

  // TODO(1ntEgr8): Temporary, remove after configs have been ported to C++
  py::class_<vajra::WorkerSequenceManagerParams>(m,
                                                 "WorkerSequenceManagerParams")
      .def(py::init<bool, std::size_t, std::size_t, std::size_t, std::size_t,
                    std::size_t, std::size_t, std::size_t>(),
           py::arg("enable_sequence_pipeline_parallel"), py::arg("block_size"),
           py::arg("num_gpu_blocks"), py::arg("max_model_len"),
           py::arg("max_num_tokens_per_kvp_group"), py::arg("rank"),
           py::arg("kvp_group_id"), py::arg("kvp_parallel_world_size"))
      .def_readonly("enable_sequence_pipeline_parallel",
                    &vajra::WorkerSequenceManagerParams::
                        enable_sequence_pipeline_parallel)
      .def_readonly("block_size",
                    &vajra::WorkerSequenceManagerParams::block_size)
      .def_readonly("num_gpu_blocks",
                    &vajra::WorkerSequenceManagerParams::num_gpu_blocks)
      .def_readonly("max_model_len",
                    &vajra::WorkerSequenceManagerParams::max_model_len)
      .def_readonly(
          "max_num_tokens_per_kvp_group",
          &vajra::WorkerSequenceManagerParams::max_num_tokens_per_kvp_group)
      .def_readonly("rank", &vajra::WorkerSequenceManagerParams::rank)
      .def_readonly("kvp_group_id",
                    &vajra::WorkerSequenceManagerParams::kvp_group_id)
      .def_readonly(
          "kvp_parallel_world_size",
          &vajra::WorkerSequenceManagerParams::kvp_parallel_world_size);

  py::class_<vajra::WorkerSequenceManager, vajra::SequenceManager,
             std::shared_ptr<vajra::WorkerSequenceManager>>(
      m, "WorkerSequenceManager")
      .def(py::init<vajra::WorkerSequenceManagerParams>(), py::arg("params"))
      .def("on_schedule_worker",
           &vajra::WorkerSequenceManager::OnScheduleWorker);
}
