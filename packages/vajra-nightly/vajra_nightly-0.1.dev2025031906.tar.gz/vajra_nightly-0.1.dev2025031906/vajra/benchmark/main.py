import logging
import os

import yaml

from vajra.benchmark.benchmark_runner import BenchmarkRunner
from vajra.benchmark.config import BenchmarkConfig
from vajra.benchmark.constants import LOGGER_FORMAT, LOGGER_TIME_FORMAT
from vajra.benchmark.utils.random import set_seeds
from vajra.logger import init_logger

logger = init_logger(__name__)


def main() -> None:
    config = BenchmarkConfig.create_from_cli_args()

    config.inference_engine_config.controller_config.replica_controller_config.model_config.load_format = (
        "dummy"
    )

    os.makedirs(config.output_dir, exist_ok=True)
    with open(os.path.join(config.output_dir, "config.yaml"), "w") as f:
        yaml.dump(config.to_dict(), f)

    logger.info(f"Starting benchmark with config: {config}")

    set_seeds(config.seed)

    log_level = getattr(logging, config.log_level.upper())
    logging.basicConfig(
        format=LOGGER_FORMAT, level=log_level, datefmt=LOGGER_TIME_FORMAT
    )

    runner = BenchmarkRunner(config)
    runner.run()


if __name__ == "__main__":
    main()
