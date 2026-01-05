"""
Production-grade logging configuration with log rotation.
Provides structured logging with JSON output and console output.
"""

import logging
import logging.config
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create logs directory if it doesn't exist
LOGS_DIR = Path(os.getenv("MCP_LOGS_DIR", "/var/log/mcp-linux-deployer"))
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configuration from environment variables with sensible defaults
LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")
MAX_BYTES = int(os.getenv("MCP_LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10 MB
BACKUP_COUNT = int(os.getenv("MCP_LOG_BACKUP_COUNT", 10))  # Keep 10 backup files
LOG_FORMAT = os.getenv("MCP_LOG_FORMAT", "detailed")  # detailed or json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        """Format log record as JSON."""
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_obj.update(record.extra_fields)

        return json.dumps(log_obj)


class DetailedFormatter(logging.Formatter):
    """Custom detailed formatter for human-readable logs."""

    def __init__(self):
        """Initialize formatter with default time format."""
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, record):
        """Format log record with detailed information."""
        # Set asctime by calling parent's formatTime
        record.asctime = self.formatTime(record, self.datefmt)

        if record.exc_info:
            return (
                f"[{record.asctime}] {record.levelname:<8} "
                f"[{record.name}:{record.funcName}:{record.lineno}] "
                f"{record.getMessage()}\n"
                f"{self.formatException(record.exc_info)}"
            )
        return (
            f"[{record.asctime}] {record.levelname:<8} "
            f"[{record.name}:{record.funcName}:{record.lineno}] "
            f"{record.getMessage()}"
        )


def setup_logging():
    """
    Configure logging with rotating file handlers and console output.

    Features:
    - Rotating file handler (size-based)
    - Timed rotating file handler (daily backup)
    - Console output for INFO+ messages
    - JSON structured logging for file output
    - Separate file for errors
    """

    # Determine formatter based on configuration
    if LOG_FORMAT == "json":
        file_formatter = JSONFormatter()
    else:
        file_formatter = DetailedFormatter()

    console_formatter = DetailedFormatter()

    # Create handlers
    handlers = {
        "console": _create_console_handler(console_formatter),
        "file": _create_file_handler(
            LOGS_DIR / "mcp-linux-deployer.log", file_formatter
        ),
        "error_file": _create_error_file_handler(
            LOGS_DIR / "mcp-linux-deployer-error.log", file_formatter
        ),
    }

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    root_logger.handlers.clear()  # Clear any existing handlers

    for handler in handlers.values():
        root_logger.addHandler(handler)

    # Set specific loggers
    logging.getLogger("fastmcp").setLevel(LOG_LEVEL)
    logging.getLogger("uvicorn").setLevel(LOG_LEVEL)
    logging.getLogger("fastapi").setLevel(LOG_LEVEL)

    return logging.getLogger("mcp-deployer")


def _create_console_handler(formatter):
    """Create console handler for stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    return handler


def _create_file_handler(log_file, formatter):
    """
    Create rotating file handler.
    Rotates when file size exceeds MAX_BYTES, keeps BACKUP_COUNT backups.
    """
    handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(formatter)
    return handler


def _create_error_file_handler(log_file, formatter):
    """
    Create rotating file handler for errors only.
    Useful for quick access to errors without sifting through info logs.
    """
    handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(logging.ERROR)
    handler.setFormatter(formatter)
    return handler


def get_logger(name):
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)


def log_operation(logger, operation_name, operation_data=None):
    """
    Context manager to log operations with timing.

    Example:
        with log_operation(logger, "build_application", {"repo": "famvest"}):
            # perform operation
            pass
    """
    from contextlib import contextmanager
    import time

    @contextmanager
    def _log_op():
        start_time = time.time()
        logger.info(f"Starting {operation_name}", extra={"extra_fields": operation_data or {}})
        try:
            yield
            duration = time.time() - start_time
            logger.info(
                f"Completed {operation_name}",
                extra={"extra_fields": {"duration_seconds": duration, **(operation_data or {})}},
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Failed {operation_name}: {str(e)}",
                exc_info=True,
                extra={"extra_fields": {"duration_seconds": duration, **(operation_data or {})}},
            )
            raise

    return _log_op()

