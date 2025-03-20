import logging
import os
from datetime import datetime
import sys

timestamp = datetime.today().strftime('%Y-%m-%d')


def configure_logger(name):
    # Retrieve log level from environment, default to INFO
    log_level = os.getenv("APP_LOG_LEVEL", "INFO").upper()

    # Create or retrieve the logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)  # Set the log level

    # Define the output format for the logger
    formatter = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(name)s - %(message)s')

    # Create a stream handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Set the log level for the handler
    handler.setLevel(log_level)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Optionally, clear any other handlers to avoid duplicate logs
    logger.handlers.clear()
    logger.addHandler(handler)

    return logger


# Exposed imports
from .utils.utils_db import DrsDB
from .utils.utils_mongo import MongoUtil
from .runner import Runner
from .healthcheck import Healthcheck

__all__ = ['DrsDB', 'MongoUtil', 'Runner', 'Healthcheck']
