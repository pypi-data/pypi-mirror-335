def print_vajra_logo():
    """
    Print a stylized VAJRA logo with a jagged, golden thunderbolt for the 'J'.
    """
    import logging

    # Explanation of ANSI sequences:
    #   \033[3m         => Start italics
    #   \033[38;5;220m  => Switch to color index 220 (a golden color)
    #   \033[39m        => Revert to default foreground color (but keep italic)
    #   \033[0m         => Reset all formatting (end italics, color, etc.)
    #

    logo = (
        "\033[3m"  # Start italic
        "\n\033[38;5;220m                    ⚡⚡⚡⚡⚡\033[39m"
        "\n\033[38;5;220m                     ⚡⚡⚡\033[39m"
        "\n\033[38;5;220m                      ⚡⚡\033[39m"
        "\n██╗   ██╗ █████╗      ⚡       ██████╗  █████╗"
        "\n██║   ██║██╔══██╗     ⚡⚡      ██╔══██╗██╔══██╗"
        "\n██║   ██║███████║      ⚡       ██████╔╝███████║"
        "\n╚██╗ ██╔╝██╔══██║      ⚡⚡      ██╔══██╗██╔══██║"
        "\n ╚████╔╝ ██║  ██║      ⚡       ██║  ██║██║  ██║"
        "\n  ╚═══╝  ╚═╝  ╚═╝       ⚡⚡     ╚═╝  ╚═╝╚═╝  ╚═╝"
        "\n\033[38;5;220m                     ⚡⚡\033[39m"
        "\n\033[38;5;220m                    ⚡\033[39m"
        "\n\033[0m"  # Reset everything
    )

    logger = logging.getLogger("vajra")
    logger.info(logo)


def pretty_print_resource_mapping(resource_mapping, logger=None):
    """Print a formatted table of resource allocations for all replicas

    Args:
        resource_mapping: Dict mapping replica IDs to lists of (node_ip, device_id) tuples
        logger: Optional logger instance to use (defaults to vajra logger)
    """
    import logging

    if logger is None:
        logger = logging.getLogger("vajra")

    if not resource_mapping:
        logger.info("No resources allocated.")
        return

    # Calculate the width needed for the node IP column
    max_ip_width = max(
        [
            len(node_ip)
            for replica_devices in resource_mapping.values()
            for node_ip, _ in replica_devices
        ]
    )
    max_ip_width = max(max_ip_width, len("Node IP"))

    # Print the header
    header = f"{'Replica ID':<10} | {'Node IP':<{max_ip_width}} | {'GPU IDs'}"
    separator = f"{'-' * 10} | {'-' * max_ip_width} | {'-' * 20}"
    logger.info(separator)
    logger.info(header)
    logger.info(separator)

    # Print each replica's resources
    for replica_id, devices in sorted(resource_mapping.items()):
        # Group devices by node for better readability
        nodes_dict = {}
        for node_ip, gpu_id in devices:
            if node_ip not in nodes_dict:
                nodes_dict[node_ip] = []
            nodes_dict[node_ip].append(gpu_id)

        # Print first line with the first node
        first_node = list(nodes_dict.keys())[0]
        gpu_str = ", ".join(str(gpu_id) for gpu_id in nodes_dict[first_node])
        logger.info(f"{replica_id:<10} | {first_node:<{max_ip_width}} | {gpu_str}")

        # Print remaining nodes if any
        for node_ip in list(nodes_dict.keys())[1:]:
            gpu_str = ", ".join(str(gpu_id) for gpu_id in nodes_dict[node_ip])
            logger.info(f"{'':<10} | {node_ip:<{max_ip_width}} | {gpu_str}")

    logger.info(separator)
