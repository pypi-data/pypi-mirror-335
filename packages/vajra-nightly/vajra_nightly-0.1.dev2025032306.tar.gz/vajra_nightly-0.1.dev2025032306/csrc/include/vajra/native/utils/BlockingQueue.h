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

#include <deque>

#include "commons/StdCommon.h"

namespace vajra {

// A simple unbounded blocking queue implemented using a lock and condition
// variable
template <typename T>
class BlockingQueue {
 public:
  BlockingQueue() : paused_(false) {}

  ~BlockingQueue() {
    {
      std::lock_guard<std::mutex> lk(mutex_);
      paused_ = true;
      q_.clear();
    }
    cv_.notify_all();
  }

  // Dequeues an element from the front of the queue. Blocks if empty.
  std::optional<T> Dequeue() noexcept {
    std::unique_lock<std::mutex> lk(mutex_);
    cv_.wait(lk, [this] { return !q_.empty() || paused_; });
    if (q_.empty() || paused_) return std::nullopt;  // pause signal
    auto elem = std::move(q_.front());
    q_.pop_front();
    return elem;
  }

  // Enqueues an element to the back of the queue.
  void Enqueue(T&& elem) noexcept {
    {
      std::lock_guard<std::mutex> lk(mutex_);
      if (paused_) return;
      q_.emplace_back(std::forward<T>(elem));
    }
    cv_.notify_one();
  }

  void Enqueue(const T& elem) noexcept {
    {
      std::lock_guard<std::mutex> lk(mutex_);
      if (paused_) return;
      q_.emplace_back(elem);
    }
    cv_.notify_one();
  }

  // Clears the contents of the queue
  void Clear() {
    {
      std::lock_guard<std::mutex> lk(mutex_);
      q_.clear();
    }
    cv_.notify_all();
  }

  // Pauses the queue, preventing threads from making updates to it. Unblocks
  // threads blocked on dequeue.
  //
  // Useful for early returning from a blocking call to `Dequeue`.
  void Pause() {
    {
      std::lock_guard<std::mutex> lk(mutex_);
      paused_ = true;
    }
    cv_.notify_all();
  }

  // Resumes the queue, allowing threads to make updates to it.
  void Resume() {
    std::lock_guard<std::mutex> lk(mutex_);
    paused_ = false;
  }

  // Returns the current size of the queue
  std::size_t Size() {
    std::lock_guard<std::mutex> lk(mutex_);
    return q_.size();
  }

 private:
  std::deque<T> q_;
  std::mutex mutex_;
  std::condition_variable cv_;
  bool paused_;
};
}  // namespace vajra
