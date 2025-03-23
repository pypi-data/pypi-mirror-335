#!/usr/bin/env python3
"""Structured logging demo - dev-friendly console renderer."""

import logging
import os

import logstruct
from logstruct import (
    StructuredFormatter,
    StructuredFormatterConfig,
    make_friendly_dump_fn,
)

logging.basicConfig(level=logging.DEBUG)
handler = logging.root.handlers[0]

if os.environ.get("DEBUG"):
    handler.formatter = StructuredFormatter(
        structured_formatter_config=StructuredFormatterConfig(
            dumps_fn=make_friendly_dump_fn(
                # Enable colours only if the handler pointed to a teletype.
                colours=isinstance(handler, logging.StreamHandler) and handler.stream.isatty()
            ),
        )
    )
else:
    handler.formatter = StructuredFormatter()

log = logstruct.getLogger(__name__)

log.debug("A debug message")
log.info("An info message")
log.warning("A warning message with stack info", stack_info=True)
log.error("An error message with data (traditional)", extra={"log": "struct", "unrepresentable": logging})
log.critical("A critical message with data (kwargs)", log="struct", unrepresentable=logging)

try:
    print(1 / 0)
except Exception:
    log.exception("Division error")
