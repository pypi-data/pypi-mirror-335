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
#include "native/transfer_engine/TransferEnginePybind.h"

#include <torch/csrc/distributed/c10d/ProcessGroup.hpp>

#include "native/configs/TransferEngineConfig.h"
#include "native/transfer_engine/backend/TransferEngineUtils.h"
#include "native/transfer_engine/factory/TransferEngineFactory.h"
#include "native/transfer_engine/interface/TransferEngine.h"
#include "native/transfer_engine/interface/TransferWork.h"
//==============================================================================
void InitTransferEnginePybindSubmodule(py::module_& pm) {
  auto m = pm.def_submodule("transfer_engine", "TransferEngine submodule");
  py::enum_<vajra::TransferBackendType>(m, "TransferBackendType")
      .value("TORCH", vajra::TransferBackendType::TORCH)
      .export_values();

  py::class_<vajra::TransferWork, std::unique_ptr<vajra::TransferWork>>(
      m, "TransferWork")
      .def("synchronize", &vajra::TransferWork::Synchronize);

  py::class_<vajra::TransferEngine, std::shared_ptr<vajra::TransferEngine>>(
      m, "TransferEngine")
      .def("async_send", &vajra::TransferEngine::AsyncSend,
           py::return_value_policy::take_ownership, py::arg("dst_replica_id"),
           py::arg("page_tensor"), py::arg("page_list"), py::arg("layer_id"))
      .def("async_recv", &vajra::TransferEngine::AsyncRecv,
           py::return_value_policy::take_ownership, py::arg("src_replica_id"),
           py::arg("page_tensor"), py::arg("page_list"), py::arg("layer_id"))
      .def("get_matching_other_global_ranks",
           &vajra::TransferEngine::GetMatchingOtherGlobalRanks,
           py::arg("other_replica_id"),
           py::arg("layer_id"))
      .def_static(
          "create_from",  // Expose the static factory method
          [](const vajra::TransferEngineConfig& transfer_engine_config) {
            std::shared_ptr<vajra::TransferEngine> engine =
                vajra::TransferEngineFactory::Create(transfer_engine_config);
            return engine;
          },
          py::return_value_policy::take_ownership,
          py::arg("transfer_engine_config"),
          "Factory method to create a TransferEngine based on config");
  py::class_<vajra::TransferEngineUtils>(m, "TransferEngineUtils")
      .def_static("copy_merge_pages_cache",
                  &vajra::TransferEngineUtils::CopyMergePagesCache);
}
//==============================================================================
