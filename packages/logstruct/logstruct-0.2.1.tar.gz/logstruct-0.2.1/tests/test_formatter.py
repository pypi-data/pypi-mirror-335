from __future__ import annotations

import inspect
import json
import logging
import time
import traceback
from dataclasses import replace
from io import StringIO
from pathlib import Path
from typing import Any, Callable, NamedTuple

import pytest
from freezegun import freeze_time

import logstruct
from logstruct import (
    CONFIG_FORMATTED_MESSAGE,
    CONFIG_RAW_MESSAGE,
    LogField,
    StructuredFormatter,
    StructuredFormatterConfig,
    add_context,
    context_scope,
    make_friendly_dump_fn,
)
from logstruct._constants import get_standard_logrecord_keys
from tests.constants import LOGGING_NAMED_ARGS

DIRPATH = str(Path(__file__).parent)


def configure_logger(logger: logging.Logger | logstruct.StructuredLogger) -> None:
    logger.setLevel(logging.DEBUG)
    logger.parent = None
    logger.handlers = [logging.StreamHandler(stream=StringIO())]


@pytest.fixture(params=[logging.getLogger, logstruct.getLogger], ids=["stdlib", "logstruct"])
def logger(request: pytest.FixtureRequest) -> logging.Logger | logstruct.StructuredLogger:
    get_logger: Callable[[str | None], logging.Logger | logstruct.StructuredLogger] = request.param

    name = request.node.function.__name__
    log = get_logger(f"test.{name}")
    configure_logger(log)
    return log


def current_line() -> int:
    caller_lineno = traceback.extract_stack()[-2].lineno
    assert caller_lineno is not None
    return caller_lineno


def log_lines(logger: logging.Logger | logstruct.StructuredLogger) -> list[dict[str, object]]:
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    stream = handler.stream
    assert isinstance(stream, StringIO)

    stream.seek(0)
    return [json.loads(line.replace(DIRPATH, "")) for line in stream]


def format_exception(exc: BaseException) -> str:
    return (
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        .replace(DIRPATH, "")
        .rstrip("\n")
    )


class ExpectedLogContents(NamedTuple):
    """Expected details of sent test logs."""

    info_log_line: int
    warning_log_line: int
    error_log_line: int
    exception_log_line: int
    stack_info_log_line: int
    formatted_exception: str
    expected_stack: str


def send_logs(logger: logging.Logger | logstruct.StructuredLogger) -> ExpectedLogContents:
    line = current_line()
    logger.info("An info message")
    logger.warning("An info message with positional args: %r", "abc")
    logger.error("An info message with data", extra={"log": "struct", "unrepresentable": {1, 2, 3}})
    try:
        print(1 / 0)
    except ZeroDivisionError as exc:
        logger.exception("Division error")
        formatted_exception = format_exception(exc)

    stack_info_log_line = current_line() + 1
    logger.critical("A critical message with stack info", stack_info=True)

    this_frame = inspect.currentframe()
    assert this_frame is not None
    caller_frame = this_frame.f_back
    expected_stack = (
        "Stack (most recent call last):\n"
        + "".join(traceback.format_stack(caller_frame)).replace(DIRPATH, "")
        + f"""\
  File "/test_formatter.py", line {stack_info_log_line}, in send_logs
    logger.critical("A critical message with stack info", stack_info=True)"""
    )
    return ExpectedLogContents(
        info_log_line=line + 1,
        warning_log_line=line + 2,
        error_log_line=line + 3,
        exception_log_line=line + 7,
        stack_info_log_line=stack_info_log_line,
        formatted_exception=formatted_exception,
        expected_stack=expected_stack,
    )


@freeze_time("2024-06-30")
def test_default_config(logger: logging.Logger | logstruct.StructuredLogger) -> None:
    formatter = StructuredFormatter()
    formatter.converter = time.gmtime
    logger.handlers[0].setFormatter(formatter)

    expected_logs = send_logs(logger)

    assert log_lines(logger) == [
        {
            "func": "send_logs",
            "level": "INFO",
            "line": expected_logs.info_log_line,
            "logger": "test.test_default_config",
            "message": "An info message",
            "time": "2024-06-30 00:00:00,000",
        },
        {
            "func": "send_logs",
            "level": "WARNING",
            "line": expected_logs.warning_log_line,
            "logger": "test.test_default_config",
            "message": "An info message with positional args: 'abc'",
            "time": "2024-06-30 00:00:00,000",
        },
        {
            "func": "send_logs",
            "level": "ERROR",
            "line": expected_logs.error_log_line,
            "logger": "test.test_default_config",
            "message": "An info message with data",
            "log": "struct",
            "time": "2024-06-30 00:00:00,000",
            "unrepresentable": "{1, 2, 3}",
        },
        {
            "exc_text": expected_logs.formatted_exception,
            "func": "send_logs",
            "level": "ERROR",
            "line": expected_logs.exception_log_line,
            "logger": "test.test_default_config",
            "message": "Division error",
            "time": "2024-06-30 00:00:00,000",
        },
        {
            "func": "send_logs",
            "level": "CRITICAL",
            "line": expected_logs.stack_info_log_line,
            "logger": "test.test_default_config",
            "message": "A critical message with stack info",
            "time": "2024-06-30 00:00:00,000",
            "stack_info": expected_logs.expected_stack,
        },
    ]


@freeze_time("2024-06-30")
def test_dev_friendly_format(logger: logging.Logger | logstruct.StructuredLogger) -> None:
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    formatter = StructuredFormatter(
        structured_formatter_config=StructuredFormatterConfig(
            dumps_fn=make_friendly_dump_fn(),
        )
    )
    formatter.converter = time.gmtime
    handler.formatter = formatter

    expected_logs = send_logs(logger)

    expected_output = f"""\
2024-06-30 00:00:00,000 INFO     test.test_dev_friendly_format:send_logs:{expected_logs.info_log_line} \
An info message
2024-06-30 00:00:00,000 WARNING  test.test_dev_friendly_format:send_logs:{expected_logs.warning_log_line} \
An info message with positional args: 'abc'
2024-06-30 00:00:00,000 ERROR    test.test_dev_friendly_format:send_logs:{expected_logs.error_log_line} \
An info message with data {{"log": "struct", "unrepresentable": "{{1, 2, 3}}"}}
2024-06-30 00:00:00,000 ERROR    test.test_dev_friendly_format:send_logs:{expected_logs.exception_log_line} \
Division error
{expected_logs.formatted_exception}
2024-06-30 00:00:00,000 CRITICAL test.test_dev_friendly_format:send_logs:{expected_logs.stack_info_log_line} \
A critical message with stack info
{expected_logs.expected_stack}
"""
    assert isinstance(handler.stream, StringIO)
    assert handler.stream.getvalue().replace(DIRPATH, "") == expected_output


@freeze_time("2024-06-30")
def test_raw_message_config(logger: logging.Logger) -> None:
    formatter = StructuredFormatter(structured_formatter_config=CONFIG_RAW_MESSAGE)
    formatter.converter = time.gmtime
    logger.handlers[0].setFormatter(formatter)

    line = current_line()
    logger.info("An info message with positional args: %r", "abc")

    assert log_lines(logger) == [
        {
            "func": "test_raw_message_config",
            "level": "INFO",
            "line": line + 1,
            "logger": "test.test_raw_message_config",
            "message": "An info message with positional args: %r",
            "positional_args": ["abc"],
            "time": "2024-06-30 00:00:00,000",
        },
    ]


@freeze_time("2024-06-30")
def test_kwargs_conflicting_with_log_record_attrs() -> None:
    """Test passing keys that would normally conflict with LogRecord attributes.

    There still exist limitations on kwargs - they cannot conflict with other log method args.
    """
    logger = logstruct.getLogger("test_kwargs_conflicting_with_log_record_attrs")
    configure_logger(logger)
    formatter = StructuredFormatter()
    formatter.converter = time.gmtime
    logger.handlers[0].setFormatter(formatter)

    kwargs = {k: 1 for k in get_standard_logrecord_keys() - LOGGING_NAMED_ARGS}
    line = current_line()
    logger.info("Message", **kwargs)  # type: ignore[arg-type]

    assert log_lines(logger) == [
        {
            "func": "test_kwargs_conflicting_with_log_record_attrs",
            "level": "INFO",
            "line": line + 1,
            "logger": "test_kwargs_conflicting_with_log_record_attrs",
            "message": "Message",
            "time": "2024-06-30 00:00:00,000",
            **kwargs,
        },
    ]


@freeze_time("2024-06-30")
def test_extras_conflicting_with_log_record_attrs() -> None:
    """Test passing extra keys that would otherwise conflict with LogRecord attributes.

    Even keys that conflict with log method args should be accepted.
    """
    logger = logstruct.getLogger("test_extras_conflicting_with_log_record_attrs")
    logger.setLevel(logging.INFO)
    logger.handlers = [logging.StreamHandler(stream=StringIO())]
    formatter = StructuredFormatter()
    formatter.converter = time.gmtime
    logger.handlers[0].setFormatter(formatter)

    extra = {k: 1 for k in get_standard_logrecord_keys() | LOGGING_NAMED_ARGS}
    line = current_line()
    logger.info("Message", extra=extra)

    assert log_lines(logger) == [
        {
            "func": "test_extras_conflicting_with_log_record_attrs",
            "level": "INFO",
            "line": line + 1,
            "logger": "test_extras_conflicting_with_log_record_attrs",
            "message": "Message",
            "time": "2024-06-30 00:00:00,000",
            **extra,
        },
    ]


@freeze_time("2024-06-30")
def test_uses_time_false(logger: logging.Logger | logstruct.StructuredLogger) -> None:
    config = replace(CONFIG_FORMATTED_MESSAGE, uses_time=False)
    logger.handlers[0].setFormatter(StructuredFormatter(structured_formatter_config=config))

    line = current_line()
    logger.info("An info message without a timestamp")

    assert "time" not in log_lines(logger)[0]
    assert log_lines(logger) == [
        {
            "func": "test_uses_time_false",
            "level": "INFO",
            "line": line + 1,
            "logger": "test.test_uses_time_false",
            "message": "An info message without a timestamp",
        },
    ]


@freeze_time("2024-06-30")
def test_defaults(logger: logging.Logger) -> None:
    defaults = {"non_standard_key": "cow", "taskName": "<no task>", "func": "<WILL_BE_OVERRIDDEN>"}
    formatter = StructuredFormatter(defaults=defaults)
    formatter.converter = time.gmtime
    logger.handlers[0].setFormatter(formatter)

    line = current_line()
    logger.info("A message")

    assert log_lines(logger) == [
        {
            "non_standard_key": "cow",
            "taskName": "<no task>",
            "func": "test_defaults",
            "level": "INFO",
            "line": line + 1,
            "logger": "test.test_defaults",
            "message": "A message",
            "time": "2024-06-30 00:00:00,000",
        },
    ]


@freeze_time("2024-06-30")
def test_custom_attribute_mapping(logger: logging.Logger) -> None:
    config = StructuredFormatterConfig(
        log_fields=(
            LogField("asctime", "ts", bool),
            LogField("name", "log"),
            LogField("levelname", "lvl"),
            LogField(lambda log_record: f"{log_record.pathname}:{log_record.lineno}", "file_line"),
            LogField("module", "mod"),
            LogField("funcName", "fn"),
            LogField("message", "event"),
            LogField("exc_text", "exception", bool),
            LogField("stack_info", "stack", bool),
        ),
    )
    formatter = StructuredFormatter(structured_formatter_config=config)
    formatter.converter = time.gmtime
    logger.handlers[0].setFormatter(formatter)

    line = current_line()
    logger.info("An info message")
    try:
        print(1 / 0)
    except ZeroDivisionError as exc:
        logger.exception("Division error")
        formatted_exception = format_exception(exc)

    assert log_lines(logger) == [
        {
            "fn": "test_custom_attribute_mapping",
            "lvl": "INFO",
            "log": "test.test_custom_attribute_mapping",
            "event": "An info message",
            "mod": "test_formatter",
            "file_line": f"/test_formatter.py:{line + 1}",
            "ts": "2024-06-30 00:00:00,000",
        },
        {
            "exception": formatted_exception,
            "fn": "test_custom_attribute_mapping",
            "lvl": "ERROR",
            "log": "test.test_custom_attribute_mapping",
            "event": "Division error",
            "mod": "test_formatter",
            "file_line": f"/test_formatter.py:{line + 5}",
            "ts": "2024-06-30 00:00:00,000",
        },
    ]


def test_extra_precedence_over_record(logger: logging.Logger) -> None:
    logger.handlers[0].setFormatter(StructuredFormatter())

    logger.info("Message")
    line = log_lines(logger)[-1]
    assert line["logger"] == logger.name

    logger.info("Message", extra={"logger": "extra"})
    line = log_lines(logger)[-1]
    assert line["logger"] == "extra"


def test_context_vars_enabled(logger: logging.Logger) -> None:
    logger.handlers[0].setFormatter(StructuredFormatter())

    def log_line() -> dict[str, object]:
        logger.info("Message")
        return log_lines(logger)[-1]

    with context_scope(x=11):
        line = log_line()
        assert line["x"] == 11

        add_context(y=22)
        line = log_line()
        assert line["x"] == 11
        assert line["y"] == 22

    line = log_line()
    assert "x" not in line
    assert "y" not in line


def test_context_vars_disabled(logger: logging.Logger) -> None:
    config = replace(CONFIG_FORMATTED_MESSAGE, get_context_fn=None)
    logger.handlers[0].setFormatter(StructuredFormatter(structured_formatter_config=config))

    with context_scope(x=1):
        logger.info("Message")
        [line] = log_lines(logger)
        assert "x" not in line


def test_context_vars_custom(logger: logging.Logger) -> None:
    context: dict[str, object] = {}

    def get_context_fn() -> dict[str, object]:
        return context

    config = replace(CONFIG_FORMATTED_MESSAGE, get_context_fn=get_context_fn)
    logger.handlers[0].setFormatter(StructuredFormatter(structured_formatter_config=config))

    context["q"] = "p"

    logger.info("Message")
    [line] = log_lines(logger)
    assert line["q"] == "p"


def test_context_precedence(logger: logging.Logger) -> None:
    logger.handlers[0].setFormatter(StructuredFormatter())

    logger.info("Message")
    line = log_lines(logger)[-1]
    assert line["logger"] == logger.name

    with context_scope(logger="context"):
        logger.info("Message")
        line = log_lines(logger)[-1]
        assert line["logger"] == "context", "Context should take precedence over record attrs"

    with context_scope(key="context"):
        logger.info("Message", extra={"key": "extra"})
        line = log_lines(logger)[-1]
        assert line["key"] == "extra", "Extra should take precedence over context"


@pytest.mark.parametrize("method", ["debug", "info", "warning", "error", "exception"])
def test_exc_info_exception(logger: logging.Logger, method: str) -> None:
    logger.handlers[0].setFormatter(StructuredFormatter())
    getattr(logger, method)("message", exc_info=ValueError("oops"))
    assert log_lines(logger)[-1]["exc_text"] == "ValueError: oops"


def some_record_func(record: logging.LogRecord) -> str:
    return ""


def some_dumps_func(data: dict[str, Any]) -> str:
    return ""


def some_context_func() -> dict[str, object]:
    return {}


def test_log_field_from_data() -> None:
    assert (LogField._from_data({"source": "asctime", "dest": "time"})) == LogField(
        source="asctime", dest="time"
    )

    assert (LogField._from_data({"source": "asctime", "dest": "time", "condition": "bool"})) == LogField(
        source="asctime", dest="time", condition=bool
    )

    assert LogField._from_data({
        "source": "tests.test_formatter.some_record_func",
        "dest": "time",
        "condition": "",
    }) == LogField(source=some_record_func, dest="time", condition=None)

    with pytest.raises(KeyError):
        LogField._from_data({"source": "asctime"})

    with pytest.raises(KeyError):
        LogField._from_data({"dest": "time"})


def test_log_field_from_data_validation() -> None:
    with pytest.raises(TypeError, match="'source' must be a string, is 1"):
        assert LogField._from_data({"source": 1, "dest": "time"})  # type:ignore[dict-item]

    with pytest.raises(TypeError, match="'dest' must be a string, is 1"):
        assert LogField._from_data({"source": "asctime", "dest": 1})  # type:ignore[dict-item]

    with pytest.raises(TypeError, match="'condition' must be a string or None, is 1"):
        assert LogField._from_data({"source": "asctime", "dest": "time", "condition": 1})  # type:ignore[dict-item]

    with pytest.raises(ImportError):
        assert LogField._from_data({"source": "nonexistent_module.nonexistent_name", "dest": "time"})

    with pytest.raises(ImportError):
        assert LogField._from_data({
            "source": "asctime",
            "dest": "time",
            "condition": "nonexistent_module.nonexistent_name",
        })


def test_structured_formatter_config_from_data() -> None:
    assert StructuredFormatterConfig._from_data({}) == StructuredFormatterConfig()
    assert StructuredFormatterConfig._from_data({
        "format_message": False,
        "uses_time": False,
        "log_fields": [
            {"source": "asctime", "dest": "time"},
            {"source": "message", "dest": "event"},
        ],
        "get_context_fn": "tests.test_formatter.some_context_func",
        "dumps_fn": "tests.test_formatter.some_dumps_func",
    }) == StructuredFormatterConfig(
        format_message=False,
        uses_time=False,
        log_fields=(
            LogField(source="asctime", dest="time"),
            LogField(source="message", dest="event"),
        ),
        get_context_fn=some_context_func,
        dumps_fn=some_dumps_func,
    )


def test_structured_formatter_config_from_data_validation() -> None:
    with pytest.raises(TypeError, match="'format_message' must be a boolean, is: 'False'"):
        StructuredFormatterConfig._from_data({
            "format_message": "False",
        })

    with pytest.raises(TypeError, match="'uses_time' must be a boolean, is: 'False'"):
        StructuredFormatterConfig._from_data({
            "uses_time": "False",
        })

    with pytest.raises(TypeError, match="'log_fields' must be a sequence of dictionaries, is: 1"):
        StructuredFormatterConfig._from_data({
            "log_fields": 1,
        })

    with pytest.raises(TypeError, match="'log_fields' must be a sequence of dictionaries, is: 'abc'"):
        StructuredFormatterConfig._from_data({"log_fields": "abc"})

    with pytest.raises(TypeError, match="'log_fields' must be a sequence of dictionaries, is: \\[12\\]"):
        StructuredFormatterConfig._from_data({"log_fields": [12]})

    with pytest.raises(TypeError, match="'get_context_fn' must be a qualified callable name, is: 12"):
        StructuredFormatterConfig._from_data({
            "get_context_fn": 12,
        })

    with pytest.raises(ImportError):
        StructuredFormatterConfig._from_data({
            "get_context_fn": "nonexistent_module.nonexistent_name",
        })

    with pytest.raises(TypeError, match="'dumps_fn' must be a qualified callable name, is: 21"):
        StructuredFormatterConfig._from_data({"dumps_fn": 21})

    with pytest.raises(ImportError):
        StructuredFormatterConfig._from_data({
            "dumps_fn": "nonexistent_module.nonexistent_name",
        })


def test_log_field_legacy_args() -> None:
    expected_record = LogField("asctime", "time")

    assert LogField(log_record_attr="asctime", struct_key="time") == expected_record
    assert LogField("asctime", struct_key="time") == expected_record


def test_log_field_bad_args() -> None:
    """Test overlapping combinations of legacy and current args."""
    with pytest.raises(AssertionError):
        LogField(source="a", log_record_attr="b")  # type: ignore[call-overload]

    with pytest.raises(AssertionError):
        LogField("a", log_record_attr="b")  # type: ignore[call-overload]

    with pytest.raises(AssertionError):
        LogField(struct_key="b", dest="c")  # type: ignore[call-overload]

    with pytest.raises(AssertionError):
        LogField("a", struct_key="b", dest="c")  # type: ignore[call-overload]

    with pytest.raises(AssertionError):
        LogField("a", log_record_attr="b", struct_key="c", dest="d")  # type: ignore[call-overload]
