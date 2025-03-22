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
namespace vajra {
//==============================================================================
struct CommInfo final {
  CommInfo(std::string distributed_init_method_param,
           std::string engine_ip_address_param,
           std::size_t enqueue_socket_port_param,
           std::size_t output_socket_port_param,
           std::size_t microbatch_socket_port_param)
      : distributed_init_method(distributed_init_method_param),
        engine_ip_address(engine_ip_address_param),
        enqueue_socket_port(enqueue_socket_port_param),
        output_socket_port(output_socket_port_param),
        microbatch_socket_port(microbatch_socket_port_param) {}

  const std::string distributed_init_method;
  const std::string engine_ip_address;
  const std::size_t enqueue_socket_port;
  const std::size_t output_socket_port;
  const std::size_t microbatch_socket_port;
};
//==============================================================================
}  // namespace vajra
//==============================================================================
