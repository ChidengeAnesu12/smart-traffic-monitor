"""
Smart Traffic & Road Safety Monitoring System
Entry point for the pipeline.
"""

import yaml
import sys
import logging
from pathlib import Path


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_logging(config: dict) -> None:
    """Configure application-level logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config["logging"]["level"]),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config["logging"]["log_file"]),
        ],
    )


def main():
    config = load_config()
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("Smart Traffic Monitor starting...")
    logger.info(f"Device: {config['model']['device']}")
    logger.info(f"Model weights: {config['model']['weights']}")
    logger.info("Environment OK. Ready for Phase 2.")


if __name__ == "__main__":
    main()