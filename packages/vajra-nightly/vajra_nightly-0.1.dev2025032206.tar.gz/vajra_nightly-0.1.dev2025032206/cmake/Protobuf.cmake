
file(GLOB PROTO_FILES "${CMAKE_CURRENT_SOURCE_DIR}/proto/*.proto")
add_library(proto-objects OBJECT "${PROTO_FILES}")

target_link_libraries(proto-objects PUBLIC protobuf::libprotobuf)

set(PROTO_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")

target_include_directories(proto-objects PUBLIC "$<BUILD_INTERFACE:${PROTO_BINARY_DIR}>")

protobuf_generate(
    TARGET proto-objects
    IMPORT_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/proto"
    PROTOC_OUT_DIR "${PROTO_BINARY_DIR}")