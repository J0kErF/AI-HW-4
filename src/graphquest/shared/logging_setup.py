"""FIFO log configuration (V3 §7.3).

Builds a rotating file logger from ``config/logging_config.json`` with a
bounded number of files (oldest deleted first — FIFO), so a long agent run
cannot fill the disk.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


def configure_logging(logging_config: dict[str, Any]) -> logging.Logger:
    """Configure and return the package root logger.

    Args:
        logging_config: The ``logging_config.json`` block.

    Returns:
        The configured ``graphquest`` logger.
    """
    log_dir = Path(logging_config.get("log_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    rotation = logging_config.get("rotation", {})

    handler = RotatingFileHandler(
        log_dir / "graphquest.log",
        maxBytes=int(rotation.get("max_bytes_per_file", 1_048_576)),
        backupCount=int(rotation.get("max_files", 10)),
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(logging_config.get("format", "%(message)s")))

    logger = logging.getLogger("graphquest")
    logger.setLevel(logging_config.get("level", "INFO"))
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger
