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
#include "native/core/tokenizer/TokenizerPybind.h"
//==============================================================================
#include <torch/extension.h>

#include "native/core/tokenizer/Tokenizer.h"
//==============================================================================
namespace vajra {
//==============================================================================
void InitTokenizerPybindClass(py::module_& m) {
  py::class_<Tokenizer, std::shared_ptr<Tokenizer>>(m, "Tokenizer")
      .def_static("from_path", &Tokenizer::FromPath)
      .def("encode", &Tokenizer::Encode)
      .def("decode", &Tokenizer::Decode)
      .def("partial_decode", &Tokenizer::PartialDecode);
}
//==============================================================================
void InitTokenizerPybindSubmodule(py::module& pm) {
  auto m = pm.def_submodule("tokenizer", "Tokenizer submodule");
  InitTokenizerPybindClass(m);
}
//==============================================================================
}  // namespace vajra
//==============================================================================
