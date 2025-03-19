from typing import Any, Type

import zmq

from vajra.utils.proto_utils import ProtobufAdapter


class ZMQHelper:

    @staticmethod
    def send_pyobj(socket: zmq.Socket, obj: Any) -> None:
        """Sends a Python object through a ZMQ Socket using protobuf serialization."""
        proto = ProtobufAdapter.to_proto(obj)
        socket.send(proto.SerializeToString())

    @staticmethod
    def recv_pyobj(socket: zmq.Socket, proto_class: Type[Any]) -> Any:
        """Receive a Protocol Buffer message from a ZMQ socket."""
        message = socket.recv()
        return ProtobufAdapter.from_proto(message, proto_class)
