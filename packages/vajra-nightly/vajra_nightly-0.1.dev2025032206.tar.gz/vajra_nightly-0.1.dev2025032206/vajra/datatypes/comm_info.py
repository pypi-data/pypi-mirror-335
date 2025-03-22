from vajra._native.datatypes import CommInfo as CommInfoC
from vajra.utils import get_ip, get_random_ports


class CommInfo:
    def __init__(self, driver_ip: str):
        # TODO(amey): Use a more robust method to initialize the workers.
        # In case port is already in use, this will fail.
        ports = get_random_ports(4)

        self.distributed_init_method = f"tcp://{driver_ip}:{ports[0]}"
        self.engine_ip_address = get_ip()
        self.enqueue_socket_port = ports[1]
        self.output_socket_port = ports[2]
        self.microbatch_socket_port = ports[3]
        self.native_handle = CommInfoC(
            self.distributed_init_method,
            self.engine_ip_address,
            self.enqueue_socket_port,
            self.output_socket_port,
            self.microbatch_socket_port,
        )
