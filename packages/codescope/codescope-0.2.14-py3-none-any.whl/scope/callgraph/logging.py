from loguru import logger
import sys

# Default configuration for scripts using the library
default_config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "level": "INFO",
        }
    ]
}

# Disable logging by default (library mode)
logger.disable("scope")


def configure_logging(config=None):
    """Configure logging for applications using scope"""
    if config is None:
        config = default_config
    logger.configure(**config)
    logger.enable("scope")
