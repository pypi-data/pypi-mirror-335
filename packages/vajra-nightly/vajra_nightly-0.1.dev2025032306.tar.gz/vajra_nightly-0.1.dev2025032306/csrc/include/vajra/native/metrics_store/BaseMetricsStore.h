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
#include "commons/StdCommon.h"
#include "native/configs/MetricsConfig.h"
#include "native/metrics_store/ChromeTracer.h"
#include "native/metrics_store/MetricType.h"
#include "native/metrics_store/Types.h"
#include "native/metrics_store/datastores/BaseCdfDataStore.h"
#include "native/metrics_store/datastores/TimeSeriesDataStore.h"
//==============================================================================
namespace vajra {
//==============================================================================

// macro to return void if metrics are disabled
#define RETURN_IF_METRICS_DISABLED()           \
  if (!IsEnabled() || !ShouldWriteMetrics()) { \
    return;                                    \
  }

using CdfDataStores =
    std::unordered_map<MetricType, std::shared_ptr<BaseCdfDataStore>>;
using TimeSeriesDataStores =
    std::unordered_map<MetricType, std::shared_ptr<TimeSeriesDataStore>>;

class BaseMetricsStore {
 public:
  // Constructor
  explicit BaseMetricsStore(const MetricsConfig& config,
                            const CdfDataStores& cdf_datastores,
                            const TimeSeriesDataStores& time_series_datastores,
                            const std::shared_ptr<ChromeTracer>& chrome_tracer);

  // Virtual destructor
  virtual ~BaseMetricsStore() = default;

  // Reset the metrics store
  void Reset();

  // Push a CPU operation metric
  void PushCpuOperationMetric(MetricType metric_type, float time);

  // Check if an operation is enabled for the given metric type
  [[nodiscard]] virtual bool IsOperationEnabled(MetricType metric_type) = 0;

  [[nodiscard]] std::shared_ptr<ChromeTracer> GetChromeTracer() const {
    return chrome_tracer_;
  }

 protected:
  // Helper function to check if metrics writing is enabled
  [[nodiscard]] bool ShouldWriteMetrics() const;

  // Helper function to check if the metrics store is enabled
  [[nodiscard]] bool IsEnabled() const;

  bool disabled_;
  const MetricsConfig config_;
  const std::string plots_dir_;

  std::vector<MetricType> gpu_op_metrics_types_;
  std::vector<MetricType> cpu_op_metrics_types_;

  CdfDataStores cdf_datastores_;
  TimeSeriesDataStores time_series_datastores_;
  std::shared_ptr<ChromeTracer> chrome_tracer_;

  std::optional<float> last_request_arrived_at_;
  std::optional<float> last_batch_end_time_;
  std::size_t num_decoded_tokens_;
  std::string scheduler_output_id_;

  // Singleton instance
  static std::shared_ptr<BaseMetricsStore> instance_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
