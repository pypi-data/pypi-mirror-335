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
// Boost headers
#include <boost/thread/concurrent_queues/sync_priority_queue.hpp>
#include <boost/thread/concurrent_queues/sync_queue.hpp>
//==============================================================================
#define PriorityQueue boost::concurrent::sync_priority_queue
#define Queue boost::concurrent::sync_queue
//==============================================================================
template <typename T>
struct is_boost_queue : std::false_type {};

template <typename T>
struct is_boost_queue<boost::sync_queue<T>> : std::true_type {};

template <typename T, typename Comp>
struct is_boost_queue<boost::sync_priority_queue<T, Comp>> : std::true_type {};
//==============================================================================
