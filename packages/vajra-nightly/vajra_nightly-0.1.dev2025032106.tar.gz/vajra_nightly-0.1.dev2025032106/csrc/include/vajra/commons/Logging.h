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

#include <fmt/format.h>
#include <fmt/ranges.h>
#include <glog/logging.h>

#include "commons/LogLevels.h"
#include "commons/StdCommon.h"
//==============================================================================
#define LOG_LEVEL LogLevel::INFO
//==============================================================================
#define LOG_DEBUG(...) \
  vajra::Logger::log(vajra::LogLevel::DEBUG, __FILE__, __LINE__, __VA_ARGS__)
#define LOG_INFO(...) \
  vajra::Logger::log(vajra::LogLevel::INFO, __FILE__, __LINE__, __VA_ARGS__)
#define LOG_WARNING(...) \
  vajra::Logger::log(vajra::LogLevel::WARNING, __FILE__, __LINE__, __VA_ARGS__)
#define LOG_ERROR(...) \
  vajra::Logger::log(vajra::LogLevel::ERROR, __FILE__, __LINE__, __VA_ARGS__)
#define LOG_CRITICAL(...) \
  vajra::Logger::log(vajra::LogLevel::CRITICAL, __FILE__, __LINE__, __VA_ARGS__)
//==============================================================================
#define EXCEPTION_FORMAT "Message: {}\nFile: {}\nLine number: {}\n"
//==============================================================================
#define RAISE_INVALID_ARGUMENTS_ERROR(format_str, ...)                      \
  LOG_CRITICAL("Invalid arguments: {}",                                     \
               fmt::format(format_str, ##__VA_ARGS__));                     \
  throw std::invalid_argument(                                              \
      fmt::format(EXCEPTION_FORMAT, fmt::format(format_str, ##__VA_ARGS__), \
                  __FILE__, __LINE__));
//==============================================================================
#define ASSERT_VALID_ARGUMENTS(x, format_str, ...)                            \
  if (!(x)) {                                                                 \
    LOG_CRITICAL("ASSERTION FAILED: {}, Message: {}", #x,                     \
                 fmt::format(format_str, ##__VA_ARGS__));                     \
    throw std::invalid_argument(                                              \
        fmt::format(EXCEPTION_FORMAT, fmt::format(format_str, ##__VA_ARGS__), \
                    __FILE__, __LINE__));                                     \
  }
//==============================================================================
#define ASSERT_VALID_RUNTIME(x, format_str, ...)                              \
  if (!(x)) {                                                                 \
    LOG_CRITICAL("ASSERTION FAILED: {}, Message: {}", #x,                     \
                 fmt::format(format_str, ##__VA_ARGS__));                     \
    throw std::runtime_error(                                                 \
        fmt::format(EXCEPTION_FORMAT, fmt::format(format_str, ##__VA_ARGS__), \
                    __FILE__, __LINE__));                                     \
  }
//==============================================================================
namespace vajra {
//==============================================================================
class Logger {
 public:
  template <typename... Args>
  static inline void log(LogLevel severity, const char* file, int line,
                         fmt::format_string<Args...> format, Args&&... args) {
    if (severity < LOG_LEVEL) {
      return;
    }

    std::string message = fmt::format(format, std::forward<Args>(args)...);
    switch (severity) {
      case LogLevel::DEBUG:
      case LogLevel::INFO:
        LOG(INFO) << "[" << file << ":" << line << "] " << message;
        break;
      case LogLevel::WARNING:
        LOG(WARNING) << "[" << file << ":" << line << "] " << message;
        break;
      case LogLevel::ERROR:
        LOG(ERROR) << "[" << file << ":" << line << "] " << message;
        break;
      case LogLevel::CRITICAL:
        LOG(ERROR) << "[" << file << ":" << line << "] " << message;
        break;
      default:
        LOG(INFO) << "[" << file << ":" << line << "] " << message;
        break;
    }
  }
};
//==============================================================================
}  // namespace vajra
//==============================================================================
