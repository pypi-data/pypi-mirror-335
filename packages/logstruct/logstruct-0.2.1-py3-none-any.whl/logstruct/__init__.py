"""Structured logging formatter."""

from __future__ import annotations

try:
    from logstruct._version import __version__, __version_tuple__
except ImportError:
    __version__ = "develop"
    __version_tuple__ = (0, 0, 0)

from logstruct._context import add_context, clear_scope, context_scope, get_context, remove_context
from logstruct._formatters import (
    CONFIG_FORMATTED_MESSAGE,
    CONFIG_RAW_MESSAGE,
    DEFAULT_DUMPS_FN,
    DEFAULT_LOG_FIELDS,
    LogField,
    StructuredFormatter,
    StructuredFormatterConfig,
    make_friendly_dump_fn,
)
from logstruct._logger import StructuredLogger, getLogger

__all__ = [
    "__version__",
    "__version_tuple__",
    "LogField",
    "StructuredFormatter",
    "StructuredFormatterConfig",
    "make_friendly_dump_fn",
    "CONFIG_FORMATTED_MESSAGE",
    "CONFIG_RAW_MESSAGE",
    "DEFAULT_DUMPS_FN",
    "DEFAULT_LOG_FIELDS",
    "StructuredLogger",
    "getLogger",
    "add_context",
    "clear_scope",
    "context_scope",
    "get_context",
    "remove_context",
]
