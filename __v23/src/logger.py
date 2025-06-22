"""
Logging Configuration for NCOS v11.5 Phoenix-Mesh

This module sets up the logging configuration for the system.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        log_format: Optional[str] = None
) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs to console only)
        log_format: Log format string
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Create file handler if log file is specified
    if log_file:
        # Ensure directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logging.info(f"Logging initialized at level {log_level}")


class SessionLogger:
    """
    Session-specific logger with context.

    This logger adds session context to log messages.
    """

    def __init__(self, session_id: str, component: str):
        """
        Initialize the session logger.

        Args:
            session_id: Session identifier
            component: Component name
        """
        self.session_id = session_id
        self.component = component
        self.logger = logging.getLogger(f"ncos.{component}")

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message with session context."""
        self.logger.debug(f"[{self.session_id}] {message}", *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message with session context."""
        self.logger.info(f"[{self.session_id}] {message}", *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message with session context."""
        self.logger.warning(f"[{self.session_id}] {message}", *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log an error message with session context."""
        self.logger.error(f"[{self.session_id}] {message}", *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log a critical message with session context."""
        self.logger.critical(f"[{self.session_id}] {message}", *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Log an exception with session context."""
        self.logger.exception(f"[{self.session_id}] {message}", *args, **kwargs)
