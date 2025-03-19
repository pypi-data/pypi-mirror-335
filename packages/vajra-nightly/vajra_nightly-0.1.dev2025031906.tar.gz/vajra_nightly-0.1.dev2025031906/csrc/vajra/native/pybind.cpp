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
#include <torch/extension.h>

#include "commons/Logging.h"
#include "native/configs/ConfigsPybind.h"
#include "native/core/CorePybind.h"
#include "native/datatypes/DatatypesPybind.h"
#include "native/metrics_store/MetricsStorePybind.h"
#include "native/model_executor/ModelExecutorPybind.h"
#include "native/scheduler/SchedulerPybind.h"
#include "native/transfer_engine/TransferEnginePybind.h"
//==============================================================================
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
  google::InitGoogleLogging("vajra-native");

  InitConfigsPybindSubmodule(m);
  InitCorePybindSubmodule(m);
  InitDatatypesPybindSubmodule(m);
  InitModelExecutorPybindSubmodule(m);
  InitMetricsStorePybindSubmodule(m);
  InitSchedulerPybindSubmodule(m);
  InitTransferEnginePybindSubmodule(m);
}
//==============================================================================
