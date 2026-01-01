"""configure logging."""
import inspect
import logging
import sys


def get_logger() -> logging.Logger:
    """Configure and return a logger that writes to console and file."""
    # Infer logger name from the calling module
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame.frame)
    logger_name = caller_module.__name__

    # Get the root logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicate logs in some environments
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
