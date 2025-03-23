#!/usr/bin/env python3
"""Structured loging demo."""

import logging

import logstruct

logging.basicConfig(level=logging.INFO)
logging.root.handlers[0].setFormatter(logstruct.StructuredFormatter())

log = logstruct.getLogger(__name__)

log.info("An info message")
log.info("An info message with stack info", stack_info=True)
log.info("An info message with data (traditional)", extra={"log": "struct", "unrepresentable": logging})
log.info("An info message with data (kwargs)", log="struct", unrepresentable=logging)

try:
    print(1 / 0)
except Exception:
    log.exception("Division error")
