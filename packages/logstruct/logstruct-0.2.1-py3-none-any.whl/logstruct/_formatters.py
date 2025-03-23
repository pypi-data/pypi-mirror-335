"""A structured logging formatter compatible with standard library logging.

A replacement for structlog, at 1% the headache structlog causes. Does not get in the way with logging, its
integrations (like Sentry). Can be assigned to any handler.

LogRecords are turned into dicts and serialised. The ``extra`` dict passed to log calls is included in the
created dict.

JSON isn't mandatory. Any str -> dict function can be passed to the config.
"""

from __future__ import annotations

import builtins
import functools
import json
import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal, Optional, cast, overload

from logstruct._constants import (
    LOG_RECORD_PREFIX,
    get_prefixed_standard_logrecord_keys,
    get_standard_logrecord_keys,
)
from logstruct._context import get_context

DEFAULT_DUMPS_FN = functools.partial(json.dumps, default=repr)


def _find_extras_in_logrecord(record: logging.LogRecord) -> dict[str, Any]:
    # We also need to undo the prefixing done in `StructuredLogger.log` in order to get around LogRecord not
    # accepting keys like "name".
    prefixed_keys = get_prefixed_standard_logrecord_keys()
    prefix_length = len(LOG_RECORD_PREFIX)
    return {
        (k if k not in prefixed_keys else k[prefix_length:]): v
        for k, v in record.__dict__.items()
        if k not in get_standard_logrecord_keys()
    }


def _import_callable(qualified_name: str) -> Callable[..., Any]:
    module_name, _, name = qualified_name.rpartition(".")
    module = builtins if module_name == "" else import_module(module_name)
    try:
        imported_callable = getattr(module, name)
    except AttributeError:
        raise ImportError(
            f"cannot import name {name!r} from {module!r} (importing object: {qualified_name!r})"
        ) from None

    if not callable(imported_callable):
        raise TypeError(f"Imported {qualified_name!r} should resolve to a callable object")

    return cast(Callable[..., Any], imported_callable)


@dataclass(frozen=True, init=False)
class LogField:
    """A mapping of a single `logging.LogRecord` attribute or callable to its corresponding output dict key.

    .. warning::
        - ``log_record_attr`` is deprecated in favour of ``source``

        - ``struct_key`` is deprecated in favour of ``dest``

        Please use ``source`` and ``dest`` names if creating LogFields from kwargs. The deprecated
        keyword args will remain supported till 1.0.


    May contain an optional inclusion ``condition``.
    """

    source: str | Callable[[logging.LogRecord], Any]
    """LogRecord attr or callable taking LogRecord and returning a string."""
    dest: str
    """Output dict key."""
    condition: Callable[[Any], bool] | None = None
    """Optional condition - if supplied, receives the value produced according to the ``source``
    attribute and decides whether to include the produced key-val in the output dict."""

    # `log_record_attr` became `source` and `struct_key` became `dest` so legacy arities needs to be
    # supported, while preventing passing of conflicting names.

    @overload  # all new names
    def __init__(
        self,
        source: str | Callable[[logging.LogRecord], Any] | None,
        dest: str | None,
        condition: Callable[[Any], bool] | None = None,
    ) -> None: ...

    @overload  # both arguments using legacy naming
    def __init__(
        self,
        *,
        log_record_attr: str | Callable[[logging.LogRecord], Any],
        struct_key: str,
        condition: Callable[[Any], bool] | None = None,
    ) -> None: ...

    @overload  # legacy-named 2nd argument
    def __init__(
        self,
        source: str | Callable[[logging.LogRecord], Any],
        *,
        struct_key: str,
        condition: Callable[[Any], bool] | None = None,
    ) -> None: ...

    def __init__(
        self,
        source: str | Callable[[logging.LogRecord], Any] | None = None,
        dest: str | None = None,
        condition: Callable[[Any], bool] | None = None,
        *,
        # Old names for backwards compat.
        log_record_attr: str | Callable[[logging.LogRecord], Any] | None = None,
        struct_key: str | None = None,
    ) -> None:
        assert (source is None) ^ (
            log_record_attr is None
        ), "Either `source` or the deprecated `log_record_attr` can be specified."
        assert (dest is None) ^ (
            struct_key is None
        ), "Either `dest` or the deprecated `struct_key` can be specified."

        object.__setattr__(self, "source", source if source is not None else log_record_attr)
        object.__setattr__(self, "dest", dest if dest is not None else struct_key)
        object.__setattr__(self, "condition", condition)

    @classmethod
    def _from_data(cls, log_field_dict: dict[str, str]) -> LogField:
        """Create a ``LogRecord`` from a dictionary.

        Example dict: ``{"source": "asctime", "dest": "time", "condition": "bool"}``.
        """
        source: str | Callable[[logging.LogRecord], Any]

        source_raw = log_field_dict["source"]
        if not isinstance(source_raw, str):
            raise TypeError(f"'source' must be a string, is {source_raw}")
        source = _import_callable(source_raw) if "." in source_raw else source_raw

        dest = log_field_dict["dest"]
        if not isinstance(dest, str):
            raise TypeError(f"'dest' must be a string, is {dest}")

        condition: Callable[[Any], bool] | None = None
        condition_name = log_field_dict.get("condition")
        if condition_name is not None and not isinstance(condition_name, str):
            raise TypeError(f"'condition' must be a string or None, is {condition_name}")
        if condition_name:
            condition = _import_callable(condition_name)

        return cls(
            source=source,
            dest=dest,
            condition=condition,
        )


DEFAULT_LOG_FIELDS = (
    LogField("asctime", "time", bool),
    LogField("name", "logger"),
    LogField("levelname", "level"),
    # Path and module not included by default because they are typically redundant with the
    # logger name.
    # LogField("pathname", "path"),
    # LogField("module", "module"),
    LogField("funcName", "func"),
    LogField("lineno", "line"),
    # Message will be computed by the formatter before mapping if `format_message` is True
    LogField("message", "message"),
    LogField("exc_text", "exc_text", bool),
    LogField("stack_info", "stack_info", bool),
)


@dataclass(frozen=True)
class StructuredFormatterConfig:
    """Config struct defining all logstruct-specific ``StructuredFormatter`` configuration.

    It allows to control stdlib conventions:

    - ``format_message``: whether log message formatting should take place

    - ``uses_time``: whether current time should be assigned to ``LogRecord.asctime``

    It defines the way the structured log message is built:

    - ``log_fields``: how ``LogRecord`` attributes are mapped to produced key-vals.

    - ``get_context_fn``: the function to pull context variables from, which get merged with
      produced key-vals.

    - ``dumps_fn``: function to serialise produced key-vals into a string

    There is no way to prevent ``StructuredLogger.log`` call keyword args from being merged into the
    produced key-vals.
    """

    format_message: bool = True
    """If True, take the message from ``record.getMessage()`` otherwise ``record.msg`` (unformatted)."""

    uses_time: bool = True
    """If True, current time will be assigned to ``LogRecord.asctime``. In ``logging``, this depends
    on the attached "Formatter style" (e.g. ``logging.PercentStyle``), which isn't useful in
    structured logging, and is therefore ignored."""

    log_fields: Sequence[LogField] = DEFAULT_LOG_FIELDS
    """
    ``log_fields`` configure how ``logging.LogRecord`` attributes map to the produced key-vals.

    A major difference from structlog is that by default the log message goes to the "message" key rather than
    "event".

    For example, this configuration:

    .. code:: python

        (
            LogField("asctime", "time", bool),
            LogField(lambda log_record: f"{log_record.pathname}:{log_record.lineno}", "loc"),
            LogField("message", "message"),
        )

    produces logs that look like (excluding formatting):

    .. code::

        {
            "time": "2025-02-09 19:03:56",
            "loc": "/path/to/file.py:30",
            "message": "A message"
        }
    """

    get_context_fn: Callable[[], dict[str, object]] | None = get_context
    """Provides `context <context_usage>` variables."""

    dumps_fn: Callable[..., str] = DEFAULT_DUMPS_FN
    """
    By default ``dumps_fn`` is :py:func:`json.dumps` which will apply :py:func:`repr` to otherwise
    unserialisable objects, however any serialiser func can be used.
    """

    @classmethod
    def _from_data(cls, config_dict: dict[str, Any]) -> StructuredFormatterConfig:
        """Load config from a dictionary source, e.g. YAML."""
        format_message = config_dict.get("format_message", True)
        if not isinstance(format_message, bool):
            raise TypeError(f"'format_message' must be a boolean, is: {config_dict['format_message']!r}")

        uses_time = config_dict.get("uses_time", True)
        if not isinstance(uses_time, bool):
            raise TypeError(f"'uses_time' must be a boolean, is: {config_dict['uses_time']!r}")

        log_fields: Sequence[LogField] = DEFAULT_LOG_FIELDS
        log_fields_dicts = config_dict.get("log_fields")
        if log_fields_dicts:
            if (
                isinstance(log_fields_dicts, Sequence)
                and not isinstance(log_fields_dicts, str)
                and all(isinstance(d, dict) for d in log_fields_dicts)
            ):
                log_fields = tuple(LogField._from_data(log_field_dict) for log_field_dict in log_fields_dicts)
            else:
                raise TypeError(f"'log_fields' must be a sequence of dictionaries, is: {log_fields_dicts!r}")

        get_context_fn: Callable[[], dict[str, object]] | None = get_context
        get_context_fn_name = config_dict.get("get_context_fn")
        if get_context_fn_name:
            if not isinstance(get_context_fn_name, str):
                raise TypeError(
                    f"'get_context_fn' must be a qualified callable name, is: {get_context_fn_name!r}"
                )
            get_context_fn = _import_callable(get_context_fn_name)

        dumps_fn: Callable[..., str] = DEFAULT_DUMPS_FN
        dumps_fn_name = config_dict.get("dumps_fn")
        if dumps_fn_name:
            if not isinstance(dumps_fn_name, str):
                raise TypeError(f"'dumps_fn' must be a qualified callable name, is: {dumps_fn_name!r}")
            dumps_fn = _import_callable(dumps_fn_name)

        return cls(
            format_message=format_message,
            uses_time=uses_time,
            log_fields=log_fields,
            get_context_fn=get_context_fn,
            dumps_fn=dumps_fn,
        )


def make_friendly_dump_fn(
    level_key: str = "level",
    logger_name_key: str = "logger",
    line_key: str = "line",
    time_key: str = "time",
    func_key: str = "func",
    message_key: str = "message",
    exc_text_key: str = "exc_text",
    stack_info_key: str = "stack_info",
    dumps_fn: Callable[..., str] = StructuredFormatterConfig.dumps_fn,
    colours: bool = False,
) -> Callable[[dict[str, object]], str]:
    """Build a function serialising structured data in a developer-friendly way.

    Default values for ``*_key`` parameters correspond to default formatter config.

    A typical message looks like:

    .. code::

        2024-08-07 23:10:06,605 INFO     __main__:<module>:35 A message {"key": "val"}

    This is not meant to be the only way to serialise logged data in development. Users can supply their own
    friendly dump function.
    """
    if colours:
        levels = {
            "DEBUG": "\033[0;1m",
            "INFO": "\033[92;1m",
            "WARNING": "\033[93;1m",
            "ERROR": "\033[91;1m",
            "CRITICAL": "\033[101;1m",
        }
        bold = "\033[1m"
        reset = "\033[0m"
    else:
        levels = {}
        bold = ""
        reset = ""

    def friendly_dump_fn(
        data: dict[str, object],
    ) -> str:
        """Serialise data in a developer-friendly way."""
        d = cast(dict[Optional[str], object], data)  # cast does not with with str | None in place of Optional

        level = d.pop(level_key, "<no level>")
        logger_name = d.pop(logger_name_key, "<no name>")
        line = d.pop(line_key, "<no line>")
        time = d.pop(time_key, "<no time>")
        func = d.pop(func_key, "<no func>")
        message = d.pop(message_key, "<no message>")
        exc_text = d.pop(exc_text_key, "")
        stack_info = d.pop(stack_info_key, "")

        newline = "\n"
        level_format = levels.get(level, "") if isinstance(level, str) else ""
        return (
            f"{time} {level_format}{level:8}{reset} {bold}{logger_name}{reset}:{func}:{line}"
            f"{' ' if message else ''}{bold}{message}{reset}"
            f"{' ' if data else ''}{dumps_fn(data) if data else ''}"
            f"{newline if exc_text else ''}{exc_text}"
            f"{newline if stack_info else ''}{stack_info}"
        )

    return friendly_dump_fn


CONFIG_FORMATTED_MESSAGE = StructuredFormatterConfig()
"""StructuredLogger configuration providing output with a formatted message."""

CONFIG_RAW_MESSAGE = StructuredFormatterConfig(
    format_message=False,
    log_fields=DEFAULT_LOG_FIELDS + (LogField("args", "positional_args", bool),),
)
"""
StructuredLogger configuration providing output with an unformatted message and separate format
args"""


class StructuredFormatter(logging.Formatter):
    """A logging formatter that turns LogRecords into structured data."""

    __config: StructuredFormatterConfig
    __defaults: Mapping[str, Any]

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
        structured_formatter_config: StructuredFormatterConfig | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialise the formatter and save config specific to `StructuredFormatter`.

        Unlike `logging.Formatter.formatTime`, the ``fmt`` and ``style``, and ``validate``
        arguments have no effect, since our goal is to write out data, not an unstructured log
        line.

        The ``defaults`` argument is supported and defines default values for the produced dict.
        We one-up logging here since, unlike `logging`, the argument is supported in Python 3.9.
        """
        # `defaults` are not passed to the base, since they would have no effect anyway (it is
        # passed to the base logger's formatting style, which we don't call).
        self.__defaults = defaults if defaults is not None else {}

        super().__init__(
            fmt=fmt,
            datefmt=datefmt,
            style=style,
            validate=validate,
            **kwargs,
        )

        if structured_formatter_config is None:
            config = CONFIG_FORMATTED_MESSAGE
        elif isinstance(structured_formatter_config, dict):
            config = StructuredFormatterConfig._from_data(structured_formatter_config)
        else:
            config = structured_formatter_config

        self.__config = config

    def usesTime(self) -> bool:
        """Check if "asctime" should be assigned to the incoming log record.

        Unlike `logging.Formatter.formatTime`, which checks if "asctime" is used in the `line format string
        <https://docs.python.org/3/library/logging.html#logging.Formatter>`_,
        `StructuredFormatter` doesn't use format strings, so `StructuredFormatterConfig.uses_time`
        is returned.
        """
        return self.__config.uses_time

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record according to the config.

        Key-value pairs are discovered in the log record, the context (unless disabled), and the extra dict
        passed to the log call. They are merged into a single dict with precedence: extras, context, record.

        Mostly a clone of ``logging.Formatter.format`` but writes structured data. The ``self.formatMessage``,
        method, which normally produces a log line prefix, is not called since record attributes are included
        as data instead. The message itself is still formatted by calling ``record.getMessage()`` if enabled
        by the config.

        The reason for mutating the record is compatibility with `logging.Formatter` which does the same
        thing.
        """
        config = self.__config

        # Unlike logging, we can disable positional argument substitution
        if config.format_message:
            record.message = record.getMessage()
        else:
            record.message = record.msg

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        # this block is copy-pasted from logging, with SIM102 fixed.
        if record.exc_info and not record.exc_text:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            # logging also mutates it, blame them
            record.exc_text = self.formatException(record.exc_info)

        structured_data = {**self.__defaults}
        for record_attr_map in config.log_fields:
            source = record_attr_map.source
            # `source` may be a str attribute or a callable producing a value from LogRecord.
            val = source(record) if callable(source) else getattr(record, source, None)

            if record_attr_map.condition is None or record_attr_map.condition(val):
                structured_data[record_attr_map.dest] = val

        if config.get_context_fn is not None:
            structured_data.update(config.get_context_fn())

        structured_data.update(_find_extras_in_logrecord(record))

        return config.dumps_fn(structured_data)
