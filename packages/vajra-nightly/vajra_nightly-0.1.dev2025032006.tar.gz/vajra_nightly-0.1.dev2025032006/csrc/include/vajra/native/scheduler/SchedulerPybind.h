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

#include <pybind11/pybind11.h>

namespace py = pybind11;

/**
 * @brief Initializes the scheduler pybind submodule
 *
 * @param m The pybind11 module to initialize
 */
void InitSchedulerPybindSubmodule(py::module& m);

/**
 * @brief Initializes KvpBatchTracker pybind bindings
 *
 * @param m The pybind11 module to initialize
 */
void InitKvpBatchTrackerPybind(py::module& m);

/**
 * @brief Initializes KvpStateTracker pybind bindings
 *
 * @param m The pybind11 module to initialize
 */
void InitKvpStateTrackerPybind(py::module& m);

/**
 * @brief Initializes BatchFormationTracker pybind bindings
 *
 * @param m The pybind11 module to initialize
 */
void InitBatchFormationTrackerPybind(py::module& m);

/**
 * @brief Initializes BatchFormationTrackerWithRuntimePrediction pybind bindings
 *
 * @param m The pybind11 module to initialize
 */
void InitBatchFormationTrackerWithRuntimePredictionPybind(py::module& m);
