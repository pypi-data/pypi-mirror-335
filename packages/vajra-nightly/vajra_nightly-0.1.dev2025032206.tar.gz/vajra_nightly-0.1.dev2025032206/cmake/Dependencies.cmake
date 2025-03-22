include(FetchContent)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.13.0.tar.gz
)

FetchContent_Declare(
  glog
  URL https://github.com/google/glog/archive/refs/tags/v0.6.0.tar.gz
)

FetchContent_Declare(
  fmt
  URL https://github.com/fmtlib/fmt/archive/refs/tags/10.1.1.tar.gz
)

FetchContent_Declare(
  json
  URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
)

FetchContent_Declare(
  tokenizers_cpp
  GIT_REPOSITORY https://github.com/mlc-ai/tokenizers-cpp.git
  GIT_TAG main # TODO(Amey): Should freeze this
)

FetchContent_Declare(
  Boost
  GIT_REPOSITORY https://github.com/boostorg/boost.git
  GIT_TAG        boost-1.78.0  # Replace with your desired Boost version
)

FetchContent_Declare(
  zmq
  GIT_REPOSITORY https://github.com/zeromq/libzmq.git
  GIT_TAG        v4.3.4
)

set(ZMQ_BUILD_TESTS OFF CACHE BOOL "Build ZeroMQ tests" FORCE)
set(ZMQ_BUILD_DRAFT_API OFF CACHE BOOL "Build ZeroMQ draft API" FORCE)

# Find Vidur package
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(Vidur REQUIRED)

find_package(protobuf CONFIG REQUIRED)

FetchContent_MakeAvailable(googletest glog fmt json tokenizers_cpp Boost zmq)
