"""
Logging configuration module.
"""

import sys
from . import __version__ as package_version

import logging
from logging.handlers import RotatingFileHandler


def success(self, message, *args, **kws):
    """
    Custom logging function for SUCCESS level messages.
    """
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


# Add a custom logging level called SUCCESS
SUCCESS_LEVEL_NUM = 25  # Level between WARNING (30) and INFO (20)
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
logging.Logger.success = success  # Bind the custom function to Logger instances


# Create the main logger for the application
logger = logging.getLogger('sbi_spec_doc')
logger.setLevel(logging.DEBUG)  # Capture all logs; filtering is done by handlers

# Define the log message format
log_formatter = logging.Formatter(
    '%(asctime)s\t%(levelname)s\t%(name)s:%(module)s:%(funcName)s:%(lineno)d\t%(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)


def create_handler(level, filter_func):
    """
    Create and configure a stream handler for a specific log level.

    Args:
        level (int): Logging level for the handler.
        filter_func (Filter): Filter class to specify which records to handle.

    Returns:
        logging.Handler: Configured stream handler.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(log_formatter)
    handler.addFilter(filter_func)
    return handler


# Filter classes for different log levels
class WarningFilter(logging.Filter):
    """Allow only WARNING level logs."""
    def filter(self, record):
        return record.levelno == logging.WARNING


class ErrorFilter(logging.Filter):
    """Allow only ERROR level logs."""
    def filter(self, record):
        return record.levelno == logging.ERROR


class InfoFilter(logging.Filter):
    """Allow only INFO level logs."""
    def filter(self, record):
        return record.levelno == logging.INFO


class CriticalFilter(logging.Filter):
    """Allow only CRITICAL level logs."""
    def filter(self, record):
        return record.levelno == logging.CRITICAL


# Create a rotating file handler to store detailed logs
file_handler = RotatingFileHandler(
    'sbi_spec_doc.log',  # Log file name
    maxBytes=1 * 1024 * 1024,    # 1 MB per file before rotation
    backupCount=5,               # Keep up to 5 backup files
    encoding='utf-8'             # Ensure proper encoding for non-ASCII logs
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)  # Log everything to the file


# Attach different handlers for various log levels to the logger
logger.addHandler(create_handler(logging.WARNING, WarningFilter()))
logger.addHandler(create_handler(logging.ERROR, ErrorFilter()))
logger.addHandler(create_handler(logging.INFO, InfoFilter()))
logger.addHandler(create_handler(logging.CRITICAL, CriticalFilter()))
logger.addHandler(file_handler)

# Example of logger usage at startup
logger.info(f"Logger initialized for SbiSpecialDocxMaster version {package_version}")
