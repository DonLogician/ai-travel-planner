"""Application logging utilities."""

from __future__ import annotations

import logging
from logging.config import dictConfig

from app.core.config import settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    log_level = settings.LOG_LEVEL.upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": log_level,
                }
            },
            "loggers": {
                "": {"handlers": ["console"], "level": log_level},
                "uvicorn": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": log_level,
                    "propagate": False,
                },
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Convenience helper to create module-level loggers."""
    return logging.getLogger(name)
