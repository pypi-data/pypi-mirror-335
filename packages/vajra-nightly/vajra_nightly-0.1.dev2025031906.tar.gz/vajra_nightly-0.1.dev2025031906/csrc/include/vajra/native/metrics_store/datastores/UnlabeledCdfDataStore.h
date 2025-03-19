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
#include "ddsketch.h"  // NOLINT
//==============================================================================
namespace vajra {
//==============================================================================
class UnlabeledCdfDataStore {
 public:
  // Default constructor with default relative accuracy
  explicit UnlabeledCdfDataStore(double relative_accuracy = 0.001);

  // Constructor with a pre-created DDSketch
  explicit UnlabeledCdfDataStore(const ddsketch::DDSketch& sketch);

  // Add a value to the sketch
  void Put(float value);

  // Merge another datastore into this one
  void Merge(const UnlabeledCdfDataStore& other);

  // Get the number of values in the sketch
  std::size_t Size() const;

  // Get the sum of all values in the sketch
  float Sum() const;

  // Get a quantile value from the sketch
  float GetQuantileValue(float quantile) const;

  // Get the minimum value
  float Min() const;

  // Get the maximum value
  float Max() const;

  // Get the count of values
  std::size_t Count() const;

  // Get the zero count
  std::size_t ZeroCount() const;

  // Get the relative accuracy
  float RelativeAccuracy() const;

  // Get serialized data as a string
  std::string GetSerializedState() const;

  // Create from serialized string
  static UnlabeledCdfDataStore FromSerializedString(
      const std::string& serialized);

 private:
  // The DDSketch instance
  ddsketch::DDSketch sketch_;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
