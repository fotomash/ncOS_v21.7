"""
Production Logging Configuration for NCOS v21
Structured, rotating logs with appropriate levels
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any
import sys

class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for production"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields if present
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id
        if hasattr(record, "workflow_id"):
            log_data["workflow_id"] = record.workflow_id
        if hasattr(record, "strategy_id"):
            log_data["strategy_id"] = record.strategy_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def configure_production_logging(
    log_dir: str = "/var/log/ncos",
    log_level: str = "INFO",
    max_bytes: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 10
) -> None:
    """
    Configure production logging with rotation and structured output
    """

    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler for systemd/docker
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # Main application log with rotation
    app_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "ncos_app.log"),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    app_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(app_handler)

    # Error log for critical issues
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "ncos_error.log"),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(error_handler)

    # Performance log for metrics
    perf_logger = logging.getLogger("performance")
    perf_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "ncos_performance.log"),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    perf_handler.setFormatter(StructuredFormatter())
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    perf_logger.propagate = False

    # Security/audit log
    audit_logger = logging.getLogger("audit")
    audit_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "ncos_audit.log"),
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    audit_handler.setFormatter(StructuredFormatter())
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False

    # Configure specific module log levels
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    root_logger.info("Production logging configured", extra={
        "log_dir": log_dir,
        "log_level": log_level,
        "max_bytes": max_bytes,
        "backup_count": backup_count
    })

# Production logging presets
LOGGING_PROFILES = {
    "production": {
        "log_level": "INFO",
        "log_dir": "/var/log/ncos",
        "max_bytes": 100 * 1024 * 1024,
        "backup_count": 10
    },
    "staging": {
        "log_level": "DEBUG",
        "log_dir": "/var/log/ncos-staging",
        "max_bytes": 50 * 1024 * 1024,
        "backup_count": 5
    },
    "development": {
        "log_level": "DEBUG",
        "log_dir": "./logs",
        "max_bytes": 10 * 1024 * 1024,
        "backup_count": 3
    }
}

def get_logger(name: str, **kwargs) -> logging.Logger:
    """
    Get a logger with optional extra fields
    """
    logger = logging.getLogger(name)

    # Create a LoggerAdapter to add extra fields
    class ContextAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            # Add any extra fields from initialization
            for key, value in self.extra.items():
                kwargs.setdefault('extra', {})[key] = value
            return msg, kwargs

    return ContextAdapter(logger, kwargs)
