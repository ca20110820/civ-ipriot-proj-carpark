from functools import wraps
from datetime import datetime
from logging import FileHandler
from logging.handlers import RotatingFileHandler
import logging
import os
import json

from smartpark.project_paths import LOG_DIR


def get_logger(log_filepath, logger_name,
               logging_level=logging.DEBUG, max_bytes=1048576, *args, **kwargs):

    # Example: get_logger("car_park.txt", "car_park_logger", logging_level=logging.DEBUG)
    handler = RotatingFileHandler(log_filepath, maxBytes=max_bytes, *args, **kwargs)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] | %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging_level)
    return logger


def class_logger(log_filepath: str, logger_name: str, *logger_args, **logger_kwargs):
    def inner(cls):
        @wraps(cls)
        def wrapper(*args, **kwargs):

            if not os.path.exists(log_filepath):
                try:
                    os.makedirs(os.path.dirname(log_filepath), exist_ok=True)
                    open(log_filepath, 'a').close()
                except OSError as e:
                    print(f"Error: {e}")

            instance = cls(*args, **kwargs)
            logger = get_logger(log_filepath, logger_name, *logger_args, **logger_kwargs)

            if not hasattr(instance, "logger"):
                setattr(instance, "logger", logger)
            return instance
        return wrapper
    return inner


def get_log_filepath(filename: str):
    return LOG_DIR / filename


def write_to_file(data_str: str, file_path: str) -> None:
    with open(file_path, 'a') as file:
        file.write(data_str + "\n")


def log_data(data_str: str, file_name: str):
    write_to_file(data_str, get_log_filepath(file_name))
