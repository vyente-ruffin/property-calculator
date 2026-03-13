"""
Centralized logger — the only logging interface for all applications.

Routes logs to the correct destination based on environment:
- No APPLICATIONINSIGHTS_CONNECTION_STRING → local JSON lines (.logs/app.log + console)
- APPLICATIONINSIGHTS_CONNECTION_STRING set → Azure Monitor via configure_azure_monitor()

IMPORTANT: Import this module BEFORE importing FastAPI, Flask, or other frameworks.
configure_azure_monitor() must run first to auto-instrument HTTP frameworks.

Usage:
    from src.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("order created")
"""

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path


# Thread-safe setup — prevents duplicate handler registration
_lock = threading.Lock()
_initialized = False

# Cached at import time so we only compute it once for stripping absolute paths
_cwd_prefix = os.getcwd() + os.sep

# OTel requires service.name to identify the app in App Insights Application Map.
# Fail loud at import time — no app should run without identifying itself.
_service_name = os.environ.get("OTEL_SERVICE_NAME")
if not _service_name:
    raise RuntimeError("OTEL_SERVICE_NAME env var is required. Set it to your app's name.")

# Log level from env, default INFO — don't ship DEBUG noise to prod
_log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)


class _JSONFormatter(logging.Formatter):
    """Converts log records to single-line JSON using OTel semantic conventions.

    Local-only formatter — when APPLICATIONINSIGHTS_CONNECTION_STRING is set,
    configure_azure_monitor() replaces this entirely with native OTel formatting.
    """

    # OTel severity mapping: Python log levels → OTel SeverityNumber
    # https://opentelemetry.io/docs/specs/otel/logs/data-model/#severity-fields
    _SEVERITY_MAP = {
        "DEBUG": 5,
        "INFO": 9,
        "WARNING": 13,
        "ERROR": 17,
        "CRITICAL": 21,
    }

    def format(self, record):
        entry = {
            "Timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "SeverityText": record.levelname,
            "SeverityNumber": self._SEVERITY_MAP.get(record.levelname, 0),
            "Body": record.getMessage(),
            "Resource": {"service.name": _service_name},
            "Attributes": {
                # Relative path only — avoids leaking directory structure in prod
                "code.filepath": os.path.relpath(record.pathname),
                "code.function": record.funcName,
                "code.lineno": record.lineno,
                "logger.name": record.name,
            },
        }
        # OTel exception semantic conventions
        if record.exc_info and record.exc_info[0]:
            entry["Attributes"]["exception.type"] = record.exc_info[0].__name__
            entry["Attributes"]["exception.message"] = str(record.exc_info[1])
            # Strip absolute cwd paths from stacktrace to avoid leaking directory structure
            entry["Attributes"]["exception.stacktrace"] = self.formatException(record.exc_info).replace(_cwd_prefix, "")
        return json.dumps(entry)


def _setup():
    """One-time logging configuration. Checks the environment and attaches
    the appropriate destination (local file + console, or Azure Monitor)."""
    global _initialized
    with _lock:
        if _initialized:
            return
        _initialized = True

    conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if conn_str:
        # Azure mode: the distro handles OTel formatting, exporting, and
        # auto-instrumentation of HTTP frameworks (FastAPI, Flask, etc.).
        # logger_name scopes export to our app's namespace only — prevents
        # SDK-internal logs from being shipped to App Insights.
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(logger_name=_service_name)
        # Set log level on the app's namespace logger — Python defaults to WARNING,
        # which silently drops INFO/DEBUG before they reach the OTel exporter.
        logging.getLogger(_service_name).setLevel(_log_level)
        return

    # Local mode: JSON lines to .logs/app.log and console (stdout)
    log_dir = Path.cwd() / ".logs"
    log_dir.mkdir(exist_ok=True)

    formatter = _JSONFormatter()

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Attach to the app's namespace logger, not root — keeps third-party noise out.
    # All child loggers (e.g. "myapp.orders") inherit these handlers automatically.
    app_logger = logging.getLogger(_service_name)
    app_logger.setLevel(_log_level)
    app_logger.addHandler(file_handler)
    app_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Returns a logger scoped under the app's namespace. Call this instead of
    logging.getLogger() directly — it ensures setup runs first and scopes
    the logger under OTEL_SERVICE_NAME to filter out third-party noise."""
    _setup()
    return logging.getLogger(f"{_service_name}.{name}")
