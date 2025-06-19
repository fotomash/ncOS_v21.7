"""Production logging utilities for NCOS v21.
Provides JSON structured logging with rotating file handlers."""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "agent_id"):
            log_record["agent_id"] = getattr(record, "agent_id")
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def configure_production_logging(
    log_dir: str,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """Configure rotating JSON loggers for the application."""

    os.makedirs(log_dir, exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to prevent duplicate logs when reconfigured
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    formatter = JsonFormatter()

    app_handler = RotatingFileHandler(
        os.path.join(log_dir, "ncos_app.log"),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)

    error_handler = RotatingFileHandler(
        os.path.join(log_dir, "ncos_error.log"),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)


def get_logger(name: str, agent_id: Optional[str] = None) -> logging.Logger:
    """Return a logger with optional ``agent_id`` context."""

    logger = logging.getLogger(name)
    if agent_id is not None:
        return logging.LoggerAdapter(logger, {"agent_id": agent_id})  # type: ignore[return-value]
    return logger
