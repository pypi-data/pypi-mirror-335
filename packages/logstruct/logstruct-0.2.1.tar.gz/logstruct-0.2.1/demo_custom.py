#!/usr/bin/env python3
"""Structured logging demo with customisation."""

import json
import logging
from functools import partial

import logstruct
from logstruct import LogField, StructuredFormatter, StructuredFormatterConfig

logging.basicConfig(level=logging.INFO)

custom_json_formatter = StructuredFormatter(
    datefmt="%Y-%m-%d %H:%M:%S",
    structured_formatter_config=StructuredFormatterConfig(
        format_message=False,
        log_fields=[
            LogField("asctime", "ts", bool),
            LogField("name", "name"),
            LogField("levelname", "level"),
            LogField("module", "module"),
            LogField("funcName", "func"),
            LogField("lineno", "line"),
            LogField("message", "event"),
            LogField("exc_text", "exc_text", bool),
            LogField("stack_info", "stack_info", bool),
            LogField("args", "positional_args", bool),
        ],
        # without `default=repr` it's very easy to cause serialisation errors
        dumps_fn=partial(json.dumps, indent=4, default=repr),
    ),
)
logging.root.handlers[0].setFormatter(custom_json_formatter)

log = logstruct.getLogger(__name__)

log.info("An info message")
log.info("An info message with stack info", stack_info=True)
log.info("An info message with data (traditional)", extra={"log": "struct", "unrepresentable": logging})
log.info("An info message with data (kwargs)", log="struct", unrepresentable=logging)

try:
    print(1 / 0)
except Exception:
    log.exception("Division error")
