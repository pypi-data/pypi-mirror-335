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
#include "native/model_executor/layers/LayersPybind.h"
//==============================================================================
#include "native/model_executor/layers/LinearLayers.h"
#include "native/model_executor/layers/NormLayers.h"
#include "native/model_executor/layers/RotaryEmbedding.h"
#include "native/model_executor/layers/attention/AttentionPybind.h"
//==============================================================================
namespace vajra {
//==============================================================================
void InitColumnParallelLinearPybindClass(py::module_& m) {
  py::class_<ColumnParallelLinear, std::shared_ptr<ColumnParallelLinear>>(
      m, "ColumnParallelLinear")
      .def(py::init<int, int, bool, int, bool, torch::Tensor,
                    std::optional<torch::Tensor>, ProcessGroupWrapperPtr>())
      .def("forward", &ColumnParallelLinear::Forward);
}
//==============================================================================
void InitRowParallelLinearPybindClass(py::module_& m) {
  py::class_<RowParallelLinear, std::shared_ptr<RowParallelLinear>>(
      m, "RowParallelLinear")
      .def(py::init<int, int, bool, bool, int, int, bool, torch::Tensor,
                    std::optional<torch::Tensor>, ProcessGroupWrapperPtr>())
      .def("forward", &RowParallelLinear::Forward);
}
//==============================================================================
void InitVocabParallelEmbeddingPybindClass(py::module_& m) {
  py::class_<VocabParallelEmbedding, std::shared_ptr<VocabParallelEmbedding>>(
      m, "VocabParallelEmbedding")
      .def(py::init<int, int, int, int, bool, int, int, int, torch::Tensor,
                    ProcessGroupWrapperPtr>())
      .def("forward", &VocabParallelEmbedding::Forward);
}
//==============================================================================
void InitRMSNormPybindClass(py::module_& m) {
  py::class_<RMSNorm, std::shared_ptr<RMSNorm>>(m, "RMSNorm")
      .def(py::init<torch::Tensor, double>())
      .def("forward", &RMSNorm::Forward);
}
//==============================================================================
void InitRotaryEmbeddingPybindClass(py::module_& m) {
  py::class_<RotaryEmbedding, std::shared_ptr<RotaryEmbedding>>(
      m, "RotaryEmbedding")
      .def(py::init<int, int, int64_t, int64_t, bool, torch::Tensor>())
      .def("forward", &RotaryEmbedding::Forward);
}
//==============================================================================
void InitLayersPybindSubmodule(py::module& pm) {
  auto m = pm.def_submodule("layers", "Layers submodule");

  InitColumnParallelLinearPybindClass(m);
  InitRowParallelLinearPybindClass(m);
  InitVocabParallelEmbeddingPybindClass(m);
  InitRMSNormPybindClass(m);
  InitRotaryEmbeddingPybindClass(m);

  InitAttentionPybindSubmodule(m);
}
//==============================================================================
}  // namespace vajra
//==============================================================================
