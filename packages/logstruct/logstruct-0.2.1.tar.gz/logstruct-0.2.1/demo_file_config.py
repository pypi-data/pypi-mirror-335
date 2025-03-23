#!/usr/bin/env python3
"""Structured logging demo with file config."""

import logging
import logging.config
from pathlib import Path

import logstruct

config_file = Path(__file__).parent / "example_config.ini"
logging.config.fileConfig(config_file, disable_existing_loggers=False)

log = logstruct.getLogger(__name__)

log.info("An info message")
log.info("An info message with stack info", stack_info=True)
log.info("An info message with data (traditional)", extra={"log": "struct", "unrepresentable": logging})
log.info("An info message with data (kwargs)", log="struct", unrepresentable=logging)

try:
    print(1 / 0)
except Exception:
    log.exception("Division error")
