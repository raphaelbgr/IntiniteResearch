"""Logging configuration with beautiful CLI output."""
import logging
from pathlib import Path
from typing import Optional
from utils.beautiful_logger import BeautifulLogger


def setup_logger(
    name: str = "InfiniteResearch",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> BeautifulLogger:
    """Setup beautiful logger with Rich console output.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        console: Enable console logging

    Returns:
        BeautifulLogger instance
    """
    return BeautifulLogger(name=name, level=level, log_file=log_file)


def get_logger(name: str = "InfiniteResearch") -> logging.Logger:
    """Get existing logger or create default.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
