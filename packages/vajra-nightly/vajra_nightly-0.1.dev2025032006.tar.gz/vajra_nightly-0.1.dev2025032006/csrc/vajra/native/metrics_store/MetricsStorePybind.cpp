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
#include "native/metrics_store/MetricsStorePybind.h"

#include "native/metrics_store/ChromeTracer.h"
#include "native/metrics_store/MetricGroups.h"
#include "native/metrics_store/MetricType.h"
#include "native/metrics_store/Types.h"
#include "native/metrics_store/datastores/LabeledCdfDataStore.h"
#include "native/metrics_store/datastores/TimeSeriesDataStore.h"
#include "native/metrics_store/datastores/UnlabeledCdfDataStore.h"
//==============================================================================
using namespace vajra;  // NOLINT
//==============================================================================
void InitMetricsStorePybindSubmodule(py::module& m) {
  auto metrics_store_module =
      m.def_submodule("metrics_store", "Metrics store module");

  // Bind the ChromeTracer class
  py::class_<ChromeTracer>(metrics_store_module, "ChromeTracer")
      .def(py::init<std::size_t, std::string>(), py::arg("replica_id"),
           py::arg("output_dir"))
      .def("put", &ChromeTracer::Put, py::arg("seq_metadata_list"),
           py::arg("tensor_parallel_rank"), py::arg("pipeline_parallel_rank"),
           py::arg("kv_parallel_rank"), py::arg("start_time"),
           py::arg("end_time"))
      .def("put_scheduler_event", &ChromeTracer::PutSchedulerEvent,
           py::arg("scheduler_id"), py::arg("seq_schedule_metadata_list"),
           py::arg("start_time"), py::arg("end_time"))
      .def("merge", &ChromeTracer::Merge, py::arg("other"))
      .def("store", &ChromeTracer::Store)
      .def("get_replica_id", &ChromeTracer::GetReplicaId)
      .def("get_output_dir", &ChromeTracer::GetOutputDir)
      .def("get_state", &ChromeTracer::GetState)
      .def(py::pickle(
          [](const ChromeTracer& tracer) {  // __getstate__
            return py::make_tuple(tracer.GetReplicaId(), tracer.GetOutputDir(),
                                  tracer.GetState());
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(t.size() == 3,
                                 "Invalid pickled state for ChromeTracer!");

            return ChromeTracer(t[0].cast<std::size_t>(),
                                t[1].cast<std::string>(),
                                t[2].cast<std::string>());
          }));

  // Bind the PlotType enum
  py::enum_<PlotType>(metrics_store_module, "PlotType")
      .value("CDF", PlotType::CDF)
      .value("HISTOGRAM", PlotType::HISTOGRAM)
      .value("TIME_SERIES", PlotType::TIME_SERIES)
      .export_values();

  // Bind the UnitType enum
  py::enum_<UnitType>(metrics_store_module, "UnitType")
      .value("MS", UnitType::MS)
      .value("SECONDS", UnitType::SECONDS)
      .value("PERCENT", UnitType::PERCENT)
      .value("COUNT", UnitType::COUNT)
      .export_values();

  // Bind the LabelType enum
  py::enum_<LabelType>(metrics_store_module, "LabelType")
      .value("BATCH", LabelType::BATCH)
      .value("REQUEST", LabelType::REQUEST)
      .export_values();

  // Bind the EntityAssociationType enum
  py::enum_<EntityAssociationType>(metrics_store_module,
                                   "EntityAssociationType")
      .value("REQUEST", EntityAssociationType::REQUEST)
      .value("BATCH", EntityAssociationType::BATCH)
      .export_values();

  // Bind the ComparisonGroupType enum
  py::enum_<ComparisonGroupType>(metrics_store_module, "ComparisonGroupType")
      .value("GPU_OPERATION_RUNTIME",
             ComparisonGroupType::GPU_OPERATION_RUNTIME)
      .value("BATCH_RUNTIME", ComparisonGroupType::BATCH_RUNTIME)
      .value("BATCH_COMPOSITION", ComparisonGroupType::BATCH_COMPOSITION)
      .value("REQUEST_RUNTIME", ComparisonGroupType::REQUEST_RUNTIME)
      .export_values();

  // Bind the Metric struct
  py::class_<Metric>(metrics_store_module, "Metric")
      .def(py::init<MetricType, UnitType, bool, PlotType,
                    std::optional<ComparisonGroupType>,
                    std::optional<EntityAssociationType>,
                    std::optional<LabelType>, bool>(),
           py::arg("type"), py::arg("unit"), py::arg("requires_label"),
           py::arg("plot_type"), py::arg("comparison_group") = std::nullopt,
           py::arg("entity_association_group") = std::nullopt,
           py::arg("label_type") = std::nullopt,
           py::arg("aggregate_time_series") = true)
      .def_readonly("type", &Metric::type)
      .def_readonly("name", &Metric::name)
      .def_readonly("unit", &Metric::unit)
      .def_readonly("requires_label", &Metric::requires_label)
      .def_readonly("plot_type", &Metric::plot_type)
      .def_readonly("comparison_group", &Metric::comparison_group)
      .def_readonly("entity_association_group",
                    &Metric::entity_association_group)
      .def_readonly("label_type", &Metric::label_type)
      .def_readonly("aggregate_time_series", &Metric::aggregate_time_series)
      .def("__str__", &Metric::ToString)
      .def("__repr__", &Metric::ToString)
      .def("__eq__", &Metric::operator==)
      .def("__ne__", &Metric::operator!=)
      .def(py::pickle(
          // __getstate__: Convert the C++ object to a Python tuple that can be
          // pickled
          [](const Metric& m) {
            return py::make_tuple(m.type, m.unit, m.requires_label, m.plot_type,
                                  m.comparison_group,
                                  m.entity_association_group, m.label_type,
                                  m.aggregate_time_series);
          },
          // __setstate__: Convert the Python tuple back to a C++ object
          [](py::tuple t) {
            if (t.size() != 8)
              throw std::runtime_error("Invalid state for Metric pickle!");

            // Create a new Metric object with the unpickled data
            return Metric(t[0].cast<MetricType>(), t[1].cast<UnitType>(),
                          t[2].cast<bool>(), t[3].cast<PlotType>(),
                          t[4].cast<std::optional<ComparisonGroupType>>(),
                          t[5].cast<std::optional<EntityAssociationType>>(),
                          t[6].cast<std::optional<LabelType>>(),
                          t[7].cast<bool>());
          }));

  // Bind the helper functions
  metrics_store_module.def("plot_type_to_string", &PlotTypeToString);
  metrics_store_module.def("unit_type_to_string", &UnitTypeToString);
  metrics_store_module.def("label_type_to_string", &LabelTypeToString);
  metrics_store_module.def("entity_association_type_to_string",
                           &EntityAssociationTypeToString);
  metrics_store_module.def("comparison_group_type_to_string",
                           &ComparisonGroupTypeToString);

  metrics_store_module.def("string_to_plot_type", &StringToPlotType);
  metrics_store_module.def("string_to_unit_type", &StringToUnitType);
  metrics_store_module.def("string_to_label_type", &StringToLabelType);
  metrics_store_module.def("string_to_entity_association_type",
                           &StringToEntityAssociationType);
  metrics_store_module.def("string_to_comparison_group_type",
                           &StringToComparisonGroupType);

  // Bind the TimeSeriesDataStore class
  py::class_<TimeSeriesDataStore>(metrics_store_module, "TimeSeriesDataStore")
      .def(py::init<>())
      .def(py::init<const std::vector<std::pair<float, float>>&>())
      .def("put", &TimeSeriesDataStore::Put, py::arg("time"), py::arg("value"))
      .def("merge", &TimeSeriesDataStore::Merge, py::arg("other"))
      .def("get_start_time", &TimeSeriesDataStore::GetStartTime)
      .def("size", &TimeSeriesDataStore::Size)
      .def("sum", &TimeSeriesDataStore::Sum)
      .def("get_data_log", &TimeSeriesDataStore::GetDataLogCopy)
      .def(py::pickle(
          [](const TimeSeriesDataStore& ts) {  // __getstate__
            // Pickle a copy of the data log
            return py::make_tuple(ts.GetDataLogCopy());
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(
                t.size() == 1,
                "Invalid pickled state for TimeSeriesDataStore!");

            // Get the data from the pickle
            auto data_log = t[0].cast<std::vector<std::pair<float, float>>>();
            // Create a new TimeSeriesDataStore with the data using the custom
            // constructor
            return TimeSeriesDataStore(data_log);
          }));

  // Bind the LabeledCdfDataStore class
  py::class_<LabeledCdfDataStore>(metrics_store_module, "LabeledCdfDataStore")
      .def(py::init<>())
      .def(py::init<const std::vector<std::pair<std::string, float>>&>())
      .def("put", &LabeledCdfDataStore::Put, py::arg("label"), py::arg("value"))
      .def("merge", &LabeledCdfDataStore::Merge, py::arg("other"))
      .def("size", &LabeledCdfDataStore::Size)
      .def("sum", &LabeledCdfDataStore::Sum)
      .def("get_data_log", &LabeledCdfDataStore::GetDataLogCopy)
      .def(py::pickle(
          [](const LabeledCdfDataStore& cdf) {  // __getstate__
            // Pickle a copy of the data log
            return py::make_tuple(cdf.GetDataLogCopy());
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(
                t.size() == 1,
                "Invalid pickled state for LabeledCdfDataStore!");

            // Get the data from the pickle
            auto data_log =
                t[0].cast<std::vector<std::pair<std::string, float>>>();
            // Create a new LabeledCdfDataStore with the data using the custom
            // constructor
            return LabeledCdfDataStore(data_log);
          }));

  // Bind the UnlabeledCdfDataStore class
  py::class_<UnlabeledCdfDataStore>(metrics_store_module,
                                    "UnlabeledCdfDataStore")
      .def(py::init<double>(), py::arg("relative_accuracy") = 0.001)
      .def("put", &UnlabeledCdfDataStore::Put, py::arg("value"))
      .def("merge", &UnlabeledCdfDataStore::Merge, py::arg("other"))
      .def("size", &UnlabeledCdfDataStore::Size)
      .def("sum", &UnlabeledCdfDataStore::Sum)
      .def("min", &UnlabeledCdfDataStore::Min)
      .def("max", &UnlabeledCdfDataStore::Max)
      .def("count", &UnlabeledCdfDataStore::Count)
      .def("zero_count", &UnlabeledCdfDataStore::ZeroCount)
      .def("get_quantile_value", &UnlabeledCdfDataStore::GetQuantileValue,
           py::arg("quantile"))
      .def(py::pickle(
          [](const UnlabeledCdfDataStore& cdf) {  // __getstate__
            // Get serialized string state
            return py::make_tuple(cdf.GetSerializedState());
          },
          [](py::tuple t) {  // __setstate__
            ASSERT_VALID_RUNTIME(
                t.size() == 1,
                "Invalid pickled state for UnlabeledCdfDataStore!");

            // Extract components from the tuple
            std::string serialized_data = t[0].cast<std::string>();

            // Create a new sketch from the serialized string
            return UnlabeledCdfDataStore::FromSerializedString(serialized_data);
          }));

  // Bind the MetricType enum
  py::enum_<MetricType>(metrics_store_module, "MetricType")
      // GPU Operations
      .value("MLP_UP_PROJ", MetricType::MLP_UP_PROJ)
      .value("MLP_UP_PROJ_ALL_GATHER", MetricType::MLP_UP_PROJ_ALL_GATHER)
      .value("MLP_ACTIVATION", MetricType::MLP_ACTIVATION)
      .value("MLP_DOWN_PROJ", MetricType::MLP_DOWN_PROJ)
      .value("MLP_DOWN_PROJ_ALL_REDUCE", MetricType::MLP_DOWN_PROJ_ALL_REDUCE)
      .value("ATTN_PRE_PROJ", MetricType::ATTN_PRE_PROJ)
      .value("ATTN_PRE_PROJ_ALL_GATHER", MetricType::ATTN_PRE_PROJ_ALL_GATHER)
      .value("ATTN_POST_PROJ", MetricType::ATTN_POST_PROJ)
      .value("ATTN_POST_PROJ_ALL_REDUCE", MetricType::ATTN_POST_PROJ_ALL_REDUCE)
      .value("ATTN_KV_CACHE_SAVE", MetricType::ATTN_KV_CACHE_SAVE)
      .value("ATTN", MetricType::ATTN)
      .value("ATTN_ROPE", MetricType::ATTN_ROPE)
      .value("ATTN_INPUT_RESHAPE", MetricType::ATTN_INPUT_RESHAPE)
      .value("ATTN_OUTPUT_RESHAPE", MetricType::ATTN_OUTPUT_RESHAPE)
      .value("EMBED_LINEAR", MetricType::EMBED_LINEAR)
      .value("EMBED_ALL_REDUCE", MetricType::EMBED_ALL_REDUCE)
      .value("LM_HEAD_LINEAR", MetricType::LM_HEAD_LINEAR)
      .value("LM_HEAD_ALL_GATHER", MetricType::LM_HEAD_ALL_GATHER)
      .value("INPUT_LAYERNORM", MetricType::INPUT_LAYERNORM)
      .value("POST_ATTENTION_LAYERNORM", MetricType::POST_ATTENTION_LAYERNORM)
      .value("NORM", MetricType::NORM)
      .value("ADD", MetricType::ADD)
      .value("NCCL_SEND", MetricType::NCCL_SEND)
      .value("NCCL_RECV", MetricType::NCCL_RECV)
      .value("MOE_GATING", MetricType::MOE_GATING)
      .value("MOE_LINEAR", MetricType::MOE_LINEAR)
      // CPU Operations
      .value("SAMPLER", MetricType::SAMPLER)
      .value("PREPARE_INPUTS", MetricType::PREPARE_INPUTS)
      .value("MODEL_EXECUTION", MetricType::MODEL_EXECUTION)
      .value("WORKER_ON_SCHEDULE_HANDLING",
             MetricType::WORKER_ON_SCHEDULE_HANDLING)
      .value("WORKER_ON_STEP_COMPLETE_HANDLING",
             MetricType::WORKER_ON_STEP_COMPLETE_HANDLING)
      .value("ATTN_BEGIN_FORWARD", MetricType::ATTN_BEGIN_FORWARD)
      // Sequence Metrics Time Distributions
      .value("REQUEST_E2E_TIME", MetricType::REQUEST_E2E_TIME)
      .value("REQUEST_INTER_ARRIVAL_DELAY",
             MetricType::REQUEST_INTER_ARRIVAL_DELAY)
      .value("REQUEST_E2E_TIME_NORMALIZED",
             MetricType::REQUEST_E2E_TIME_NORMALIZED)
      .value("REQUEST_E2E_TIME_PIECEWISE_NORMALIZED",
             MetricType::REQUEST_E2E_TIME_PIECEWISE_NORMALIZED)
      .value("REQUEST_EXECUTION_TIME", MetricType::REQUEST_EXECUTION_TIME)
      .value("REQUEST_EXECUTION_TIME_NORMALIZED",
             MetricType::REQUEST_EXECUTION_TIME_NORMALIZED)
      .value("REQUEST_PREEMPTION_TIME", MetricType::REQUEST_PREEMPTION_TIME)
      .value("REQUEST_SCHEDULING_DELAY", MetricType::REQUEST_SCHEDULING_DELAY)
      .value("REQUEST_EXECUTION_PLUS_PREEMPTION_TIME",
             MetricType::REQUEST_EXECUTION_PLUS_PREEMPTION_TIME)
      .value("REQUEST_EXECUTION_PLUS_PREEMPTION_TIME_NORMALIZED",
             MetricType::REQUEST_EXECUTION_PLUS_PREEMPTION_TIME_NORMALIZED)
      .value("PREFILL_TIME_E2E", MetricType::PREFILL_TIME_E2E)
      .value("PREFILL_TIME_E2E_NORMALIZED",
             MetricType::PREFILL_TIME_E2E_NORMALIZED)
      .value("PREFILL_TIME_E2E_PIECEWISE_NORMALIZED",
             MetricType::PREFILL_TIME_E2E_PIECEWISE_NORMALIZED)
      .value("PREFILL_TIME_EXECUTION_PLUS_PREEMPTION",
             MetricType::PREFILL_TIME_EXECUTION_PLUS_PREEMPTION)
      .value("PREFILL_TIME_EXECUTION_PLUS_PREEMPTION_NORMALIZED",
             MetricType::PREFILL_TIME_EXECUTION_PLUS_PREEMPTION_NORMALIZED)
      .value("DECODE_TIME_EXECUTION_PLUS_PREEMPTION_NORMALIZED",
             MetricType::DECODE_TIME_EXECUTION_PLUS_PREEMPTION_NORMALIZED)
      // Sequence Metrics Histograms
      .value("REQUEST_NUM_TOKENS", MetricType::REQUEST_NUM_TOKENS)
      .value("REQUEST_PREFILL_TOKENS", MetricType::REQUEST_PREFILL_TOKENS)
      .value("REQUEST_DECODE_TOKENS", MetricType::REQUEST_DECODE_TOKENS)
      .value("REQUEST_PD_RATIO", MetricType::REQUEST_PD_RATIO)
      .value("REQUEST_NUM_RESTARTS", MetricType::REQUEST_NUM_RESTARTS)
      .value("REQUEST_NUM_PAUSES", MetricType::REQUEST_NUM_PAUSES)
      .value("REQUEST_NUM_IGNORED", MetricType::REQUEST_NUM_IGNORED)
      // Batch Metrics Count Distributions
      .value("BATCH_NUM_TOKENS", MetricType::BATCH_NUM_TOKENS)
      .value("BATCH_NUM_PREFILL_TOKENS", MetricType::BATCH_NUM_PREFILL_TOKENS)
      .value("BATCH_NUM_DECODE_TOKENS", MetricType::BATCH_NUM_DECODE_TOKENS)
      .value("BATCH_SIZE", MetricType::BATCH_SIZE)
      // Batch Metrics Time Distributions
      .value("BATCH_EXECUTION_TIME", MetricType::BATCH_EXECUTION_TIME)
      .value("INTER_BATCH_DELAY", MetricType::INTER_BATCH_DELAY)
      // Token Metrics Time Distributions
      .value("DECODE_TOKEN_EXECUTION_PLUS_PREEMPTION_TIME",
             MetricType::DECODE_TOKEN_EXECUTION_PLUS_PREEMPTION_TIME)
      // Completion Metrics Time Series
      .value("REQUEST_ARRIVED", MetricType::REQUEST_ARRIVED)
      .value("REQUEST_COMPLETED", MetricType::REQUEST_COMPLETED)
      .value("PREFILL_COMPLETED", MetricType::PREFILL_COMPLETED)
      .value("DECODE_COMPLETED", MetricType::DECODE_COMPLETED)
      .export_values();

  // Bind the MetricType conversion functions
  metrics_store_module.def("metric_type_to_string", &MetricTypeToString);
  metrics_store_module.def("string_to_metric_type", &StringToMetricType);

  // Bind the metric getter functions
  metrics_store_module.def("get_gpu_operation_metrics_types",
                           &GetGpuOperationMetricsTypes);
  metrics_store_module.def("get_gpu_operation_metrics", &GetGpuOperationMetrics,
                           py::arg("requires_label") = false);

  metrics_store_module.def("get_cpu_operation_metrics_types",
                           &GetCpuOperationMetricsTypes);
  metrics_store_module.def("get_cpu_operation_metrics", &GetCpuOperationMetrics,
                           py::arg("requires_label") = false);

  metrics_store_module.def("get_sequence_time_distribution_metrics_types",
                           &GetSequenceTimeDistributionMetricsTypes);
  metrics_store_module.def("get_sequence_time_distribution_metrics",
                           &GetSequenceTimeDistributionMetrics);

  metrics_store_module.def("get_sequence_histogram_metrics_types",
                           &GetSequenceHistogramMetricsTypes);
  metrics_store_module.def("get_sequence_histogram_metrics",
                           &GetSequenceHistogramMetrics);

  metrics_store_module.def("get_batch_count_distribution_metrics_types",
                           &GetBatchCountDistributionMetricsTypes);
  metrics_store_module.def("get_batch_count_distribution_metrics",
                           &GetBatchCountDistributionMetrics,
                           py::arg("requires_label") = false);

  metrics_store_module.def("get_batch_time_distribution_metrics_types",
                           &GetBatchTimeDistributionMetricsTypes);
  metrics_store_module.def("get_batch_time_distribution_metrics",
                           &GetBatchTimeDistributionMetrics,
                           py::arg("requires_label") = false);

  metrics_store_module.def("get_token_time_distribution_metrics_types",
                           &GetTokenTimeDistributionMetricsTypes);
  metrics_store_module.def("get_token_time_distribution_metrics",
                           &GetTokenTimeDistributionMetrics);

  metrics_store_module.def("get_completion_time_series_metrics_types",
                           &GetCompletionTimeSeriesMetricsTypes);
  metrics_store_module.def("get_completion_time_series_metrics",
                           &GetCompletionTimeSeriesMetrics);

  metrics_store_module.def("get_all_metrics", &GetAllMetrics,
                           py::arg("write_metrics") = true,
                           py::arg("keep_individual_batch_metrics") = false,
                           py::arg("enable_gpu_op_level_metrics") = false,
                           py::arg("enable_cpu_op_level_metrics") = false);
}
//==============================================================================
