#!/usr/bin/env python3
"""Structured logging demo - context."""

import logging

import logstruct

logging.basicConfig(level=logging.INFO)
# Context in StructuredFormatter is enabled by default.
logging.root.handlers[0].setFormatter(logstruct.StructuredFormatter())

log = logstruct.getLogger(__name__)

log.info("No context")

# `context_scope` manages a task-safe stack of context variables.
with logstruct.context_scope(
    outer="outer",
    will_be_redefined="outer",
):
    log.info("Outer context")

    # Context added with `add_context` will be cleaned automatically when exiting the scope.
    logstruct.add_context(more_context="pushed")
    logstruct.add_context(even_more_context="pushed")
    log.info("More context")

    # Context variables can be removed.
    logstruct.remove_context("even_more_context")
    log.info("A little less context")

    with logstruct.context_scope(
        will_be_redefined="inner",
        inner="inner",
    ):
        log.info("Inner context")

log.info("No context")

# `context_scope` is optional.
logstruct.add_context(val1=1, val2=2)
log.info("Global context - 2 vars")
logstruct.remove_context("val1")
log.info("Global context - 1 var")
logstruct.clear_scope()
log.info("No context")
