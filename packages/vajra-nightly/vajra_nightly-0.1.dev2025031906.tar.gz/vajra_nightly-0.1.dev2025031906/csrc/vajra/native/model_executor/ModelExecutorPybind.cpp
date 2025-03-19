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
#include "native/model_executor/ModelExecutorPybind.h"

#include <torch/csrc/distributed/c10d/ProcessGroup.hpp>

#include "native/model_executor/layers/LinearLayers.h"
#include "native/model_executor/layers/NormLayers.h"
#include "native/model_executor/layers/RotaryEmbedding.h"
#include "native/model_executor/layers/attention/FlashinferAttentionWrapper.h"
#include "native/model_executor/layers/attention/SequenceArrangement.h"
#include "native/model_executor/layers/attention/flashinfer/BatchPrefillWithPagedKVCacheWrapper.h"
#include "native/model_executor/models/Llama.h"
#include "native/model_executor/parallel_utils/ProcessGroupWrapper.h"
//==============================================================================
namespace pybind11 {
namespace detail {
template <>
struct type_caster<std::set<int>> {
 public:
  PYBIND11_TYPE_CASTER(std::set<int>, _("Set[int]"));
  bool load(handle src, bool) {
    if (!py::isinstance<py::set>(src) && !py::isinstance<py::frozenset>(src))
      return false;
    for (auto item : src) {
      if (!py::isinstance<py::int_>(item)) return false;
      value.insert(item.cast<int>());
    }
    return true;
  }
  static handle cast(const std::set<int>& src, return_value_policy, handle) {
    py::set s;
    for (int v : src) s.add(py::cast(v));
    return s.release();
  }
};
}  // namespace detail
}  // namespace pybind11
//==============================================================================
void InitModelExecutorPybindSubmodule(py::module_& pm) {
  auto m = pm.def_submodule("model_executor", "Model executor submodule");

  pybind11::class_<vajra::LlamaMLP, std::shared_ptr<vajra::LlamaMLP>>(
      m, "LlamaMLP")
      .def(pybind11::init<std::shared_ptr<vajra::ColumnParallelLinear>,
                          std::shared_ptr<vajra::RowParallelLinear>>())
      .def("forward", &vajra::LlamaMLP::Forward);

  pybind11::class_<vajra::LlamaAttention,
                   std::shared_ptr<vajra::LlamaAttention>>(m, "LlamaAttention")
      .def(pybind11::init<int, int, float,
                          const std::shared_ptr<vajra::ColumnParallelLinear>,
                          const std::shared_ptr<vajra::RowParallelLinear>,
                          const std::shared_ptr<vajra::RotaryEmbedding>>())
      .def("forward", &vajra::LlamaAttention::Forward);

  pybind11::class_<vajra::LlamaDecoderLayer,
                   std::shared_ptr<vajra::LlamaDecoderLayer>>(
      m, "LlamaDecoderLayer")
      .def(pybind11::init<const std::shared_ptr<vajra::LlamaAttention>,
                          const std::shared_ptr<vajra::LlamaMLP>,
                          const std::shared_ptr<vajra::RMSNorm>,
                          const std::shared_ptr<vajra::RMSNorm>>())
      .def("forward", &vajra::LlamaDecoderLayer::Forward);

  pybind11::class_<vajra::LlamaModel, std::shared_ptr<vajra::LlamaModel>>(
      m, "LlamaModel")
      .def(
          pybind11::init<const std::shared_ptr<vajra::VocabParallelEmbedding>,
                         std::vector<std::shared_ptr<vajra::LlamaDecoderLayer>>,
                         std::shared_ptr<vajra::RMSNorm>>())
      .def("forward", &vajra::LlamaModel::Forward);

  pybind11::class_<vajra::ColumnParallelLinear,
                   std::shared_ptr<vajra::ColumnParallelLinear>>(
      m, "ColumnParallelLinear")
      .def(pybind11::init<int, int, bool, int, bool, torch::Tensor,
                          std::optional<torch::Tensor>,
                          std::shared_ptr<vajra::ProcessGroupWrapper>>())
      .def("forward", &vajra::ColumnParallelLinear::Forward);

  pybind11::class_<vajra::RowParallelLinear,
                   std::shared_ptr<vajra::RowParallelLinear>>(
      m, "RowParallelLinear")
      .def(pybind11::init<int, int, bool, bool, int, int, bool, torch::Tensor,
                          std::optional<torch::Tensor>,
                          std::shared_ptr<vajra::ProcessGroupWrapper>>())
      .def("forward", &vajra::RowParallelLinear::Forward);

  pybind11::class_<vajra::VocabParallelEmbedding,
                   std::shared_ptr<vajra::VocabParallelEmbedding>>(
      m, "VocabParallelEmbedding")
      .def(
          pybind11::init<int, int, int, int, bool, int, int, int, torch::Tensor,
                         std::shared_ptr<vajra::ProcessGroupWrapper>>())
      .def("forward", &vajra::VocabParallelEmbedding::Forward);

  pybind11::class_<vajra::RMSNorm, std::shared_ptr<vajra::RMSNorm>>(m,
                                                                    "RMSNorm")
      .def(pybind11::init<torch::Tensor, double>())
      .def("forward", &vajra::RMSNorm::Forward);

  pybind11::class_<vajra::RotaryEmbedding,
                   std::shared_ptr<vajra::RotaryEmbedding>>(m,
                                                            "RotaryEmbedding")
      .def(pybind11::init<int, int, int64_t, int64_t, bool, torch::Tensor>())
      .def("forward", &vajra::RotaryEmbedding::Forward);

  pybind11::class_<vajra::ProcessGroupWrapper,
                   std::shared_ptr<vajra::ProcessGroupWrapper>>(
      m, "ProcessGroupWrapper")
      .def(pybind11::init<c10::intrusive_ptr<c10d::ProcessGroup>,
                          c10::intrusive_ptr<c10d::ProcessGroup>,
                          c10::intrusive_ptr<c10d::ProcessGroup>>())
      .def("get_tensor_model_parallel_group",
           &vajra::ProcessGroupWrapper::GetTensorModelParallelGroup)
      .def("get_pipeline_model_parallel_group",
           &vajra::ProcessGroupWrapper::GetPipelineModelParallelGroup)
      .def("get_kv_parallel_group",
           &vajra::ProcessGroupWrapper::GetKvParallelGroup);

  pybind11::class_<vajra::FlashinferAttentionWrapper,
                   std::shared_ptr<vajra::FlashinferAttentionWrapper>>(
      m, "FlashinferAttentionWrapper")
      .def(pybind11::init<std::size_t, std::size_t, std::size_t, std::size_t,
                          torch::Device>(),
           py::arg("num_q_heads"), py::arg("num_kv_heads"), py::arg("head_dim"),
           py::arg("block_size"), py::arg("device"))
      .def("begin_forward", &vajra::FlashinferAttentionWrapper::BeginForward,
           py::arg("seq_metadata_list"))
      .def("end_forward", &vajra::FlashinferAttentionWrapper::EndForward)
      .def("run", &vajra::FlashinferAttentionWrapper::Run)
      .def("save_kv_cache", &vajra::FlashinferAttentionWrapper::SaveKVCache)
      .def_property_readonly("num_q_tokens",
                             &vajra::FlashinferAttentionWrapper::GetNumQTokens)
      .def_property_readonly(
          "should_save_kv_cache",
          &vajra::FlashinferAttentionWrapper::ShouldSaveKVCache)
      .def_property_readonly(
          "kvp_seqs_offset",
          &vajra::FlashinferAttentionWrapper::GetKvpSeqsOffset)
      .def_property_readonly(
          "kvp_seqs_qo_indptr",
          &vajra::FlashinferAttentionWrapper::GetKvpSeqsQoIndptr)
      .def_property_readonly(
          "kvp_seqs_group_ids",
          &vajra::FlashinferAttentionWrapper::GetKvpSeqsGroupIds)
      .def_property_readonly(
          "slot_mapping_tensor",
          &vajra::FlashinferAttentionWrapper::GetSlotMappingTensor)
      .def_property_readonly(
          "qo_indptr_tensor",
          &vajra::FlashinferAttentionWrapper::GetQoIndptrTensor)
      .def_property_readonly(
          "kv_page_indptr_tensor",
          &vajra::FlashinferAttentionWrapper::GetKvPageIndptrTensor)
      .def_property_readonly(
          "kv_page_indices_tensor",
          &vajra::FlashinferAttentionWrapper::GetKvPageIndicesTensor)
      .def_property_readonly(
          "kv_last_page_len_tensor",
          &vajra::FlashinferAttentionWrapper::GetKvLastPageLenTensor);

  pybind11::class_<vajra::SequenceArrangement,
                   std::shared_ptr<vajra::SequenceArrangement>>(
      m, "SequenceArrangement")
      .def(pybind11::init<>())
      .def("check_arrangement_and_extend",
           &vajra::SequenceArrangement::CheckArrangementAndExtend)
      .def("get_arranged", &vajra::SequenceArrangement::GetArranged)
      .def("get_splits", &vajra::SequenceArrangement::GetSplits)
      .def("get_num_splits", &vajra::SequenceArrangement::GetNumSplits);

  // Create flashinfer submodule
  auto flashinfer =
      m.def_submodule("flashinfer", "Flashinfer integration module");

  pybind11::class_<
      vajra::flashinfer::BatchPrefillWithPagedKVCacheWrapper,
      std::shared_ptr<vajra::flashinfer::BatchPrefillWithPagedKVCacheWrapper>>(
      flashinfer, "BatchPrefillWithPagedKVCacheWrapper")
      .def(pybind11::init<torch::Tensor, std::string, std::string>(),
           pybind11::arg("float_workspace_buffer"),
           pybind11::arg("kv_layout") = "NHD",
           pybind11::arg("backend") = "auto")
      .def(
          "plan", &vajra::flashinfer::BatchPrefillWithPagedKVCacheWrapper::Plan,
          pybind11::arg("qo_indptr"), pybind11::arg("paged_kv_indptr"),
          pybind11::arg("paged_kv_indices"),
          pybind11::arg("paged_kv_last_page_len"),
          pybind11::arg("num_qo_heads"), pybind11::arg("num_kv_heads"),
          pybind11::arg("head_dim_qk"), pybind11::arg("page_size"),
          pybind11::arg("non_blocking") = false, pybind11::arg("causal") = true,
          pybind11::arg("head_dim_vo") = std::nullopt,
          pybind11::arg("custom_mask") = std::nullopt,
          pybind11::arg("packed_custom_mask") = std::nullopt,
          pybind11::arg("pos_encoding_mode") = "NONE",
          pybind11::arg("use_fp16_qk_reduction") = false,
          pybind11::arg("sm_scale") = std::nullopt,
          pybind11::arg("window_left") = -1,
          pybind11::arg("logits_soft_cap") = std::nullopt,
          pybind11::arg("rope_scale") = std::nullopt,
          pybind11::arg("rope_theta") = std::nullopt,
          pybind11::arg("q_data_type") = "float16",
          pybind11::arg("kv_data_type") = std::nullopt)
      .def("run", &vajra::flashinfer::BatchPrefillWithPagedKVCacheWrapper::Run,
           pybind11::arg("q"), pybind11::arg("paged_kv_cache"),
           pybind11::arg("k_scale") = std::nullopt,
           pybind11::arg("v_scale") = std::nullopt,
           pybind11::arg("out") = std::nullopt,
           pybind11::arg("lse") = std::nullopt,
           pybind11::arg("return_lse") = false);
}
//==============================================================================
