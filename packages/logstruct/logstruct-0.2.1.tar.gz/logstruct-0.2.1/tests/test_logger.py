from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

from logstruct import StructuredLogger, getLogger
from logstruct._constants import LOG_RECORD_PREFIX, get_standard_logrecord_keys
from tests.constants import LOGGING_NAMED_ARGS

log = getLogger("a_logger")


@pytest.fixture
def caplog_all(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    """Capture all logs by setting the root log level to NOTSET."""
    caplog.set_level(logging.NOTSET)
    return caplog


def test_getlogger_identity() -> None:
    assert getLogger("a") is getLogger("a")


def test_getlogger_underlying_stdlib_logger() -> None:
    name = "a"
    logger = getLogger(name)
    assert isinstance(logger, StructuredLogger)
    assert isinstance(logger.logger, logging.Logger)
    assert logger.logger.name == name


@pytest.mark.parametrize(
    "log_method", [log.debug, log.info, log.warning, log.error, log.exception, log.critical]
)
def test_structured_logger_kwargs(log_method: Any, caplog_all: pytest.LogCaptureFixture) -> None:
    """Ensure that arbitrary kwargs end in log records as attributes.

    This is the way the `extra` arg is handled by default, which is a "protocol" this library complies to.
    """
    log_method("A message %r", "positional_arg", arg1="val1", arg2=["val2"], extra={"extra": 1})
    assert len(caplog_all.records) == 1
    [record] = caplog_all.records
    assert record.arg1 == "val1"  # type: ignore[attr-defined]
    assert record.arg2 == ["val2"]  # type: ignore[attr-defined]
    assert record.extra == 1  # type: ignore[attr-defined]


def test_name_set_get() -> None:
    log = getLogger("test_name_set_get")
    assert log.name == "test_name_set_get"
    assert log.logger.name == "test_name_set_get"

    log.name = "x"
    assert log.name == "x"
    assert log.logger.name == "x"


def test_log_level_set_get() -> None:
    log = getLogger("test_log_level_set_get")
    assert log.logger.level == logging.NOTSET
    assert log.level == logging.NOTSET

    # Change the log level by using the StructuredLogger property
    log.setLevel(logging.INFO)
    assert log.level == logging.INFO
    assert log.logger.level == logging.INFO

    # Change the log level in the undelying logger
    log.logger.setLevel(logging.WARNING)
    assert log.level == logging.WARNING


def test_log_is_enabled_for() -> None:
    log = getLogger("test_log_get_effective_level")
    log.parent = None  # Detach the parent, so the effective level isn't affected by it.

    assert log.logger.level == logging.NOTSET
    # not checking `log.isEnabledFor(logging.NOTSET)` because it's globally disabled by `logging.disable`.

    log.setLevel(logging.INFO)
    assert not log.isEnabledFor(logging.NOTSET)
    assert log.isEnabledFor(logging.INFO)

    log.setLevel(logging.WARNING)
    assert not log.isEnabledFor(logging.INFO)
    assert log.isEnabledFor(logging.WARNING)


def test_log_parent_get_set() -> None:
    log = getLogger("test_log_parent_get_set")
    assert log.parent is logging.root
    assert log.logger.parent is logging.root

    parent_log = logging.getLogger("test_log_parent_get_set_parent")
    log.parent = parent_log
    assert log.parent is parent_log
    assert log.logger.parent is parent_log


@pytest.mark.parametrize(
    "logger_level, parent_level, effective_level",
    [
        # The first set (non-NOTSET) log level should count as the effective log level.
        (logging.NOTSET, logging.INFO, logging.INFO),
        (logging.DEBUG, logging.NOTSET, logging.DEBUG),
        (logging.DEBUG, logging.INFO, logging.DEBUG),
        (logging.WARNING, logging.DEBUG, logging.WARNING),
        (logging.DEBUG, logging.ERROR, logging.DEBUG),
    ],
)
def test_log_get_effective_level(logger_level: int, parent_level: int, effective_level: int) -> None:
    log = getLogger("test_log_get_effective_level")
    parent_log = logging.getLogger("test_log_get_effective_level_parent")

    # Attach a parent we can control.
    log.parent = parent_log
    parent_log.parent = None

    log.setLevel(logger_level)
    parent_log.setLevel(parent_level)

    assert log.getEffectiveLevel() == effective_level
    assert log.logger.getEffectiveLevel() == effective_level


def test_log_handlers() -> None:
    log = getLogger("test_log_handlers")
    log.parent = None  # remove the parent so its log level doesn't get cached

    assert log.handlers == []
    assert log.logger.handlers == []

    # Add a logger by appending to the `handlers` list.
    stream_1 = StringIO()
    handler_1 = logging.StreamHandler(stream=stream_1)
    log.handlers.append(handler_1)

    assert log.handlers == [handler_1]
    assert log.logger.handlers == [handler_1]
    log.info("Message 1")
    stream_1.seek(0)
    # It may seem strange that the message isn't structured. That's because we don't use the
    # StructuredFormatter here.
    assert stream_1.readlines() == ["Message 1\n"]

    # Add a logger by assigning to the `handlers` property.
    stream_2 = StringIO()
    handler_2 = logging.StreamHandler(stream=stream_2)
    log.handlers = [handler_2]
    assert log.handlers == [handler_2]
    assert log.logger.handlers == [handler_2]
    log.info("Message 2")
    stream_2.seek(0)
    assert stream_2.readlines() == ["Message 2\n"]


def test_log_level_log(caplog_all: pytest.LogCaptureFixture) -> None:
    log = getLogger("test_log_level_log")
    assert log.level == logging.NOTSET

    log.debug("A debug message")
    assert len(caplog_all.records) == 1
    assert caplog_all.records[-1].message == "A debug message"

    log.setLevel(logging.INFO)

    log.debug("Another debug message")
    assert len(caplog_all.records) == 1
    log.info("An info message")
    assert len(caplog_all.records) == 2
    assert caplog_all.records[-1].message == "An info message"

    log.setLevel(logging.WARNING)

    log.debug("Another debug message")
    log.info("Another info message")
    assert len(caplog_all.records) == 2
    log.warning("A warning message")
    assert len(caplog_all.records) == 3
    assert caplog_all.records[-1].message == "A warning message"


def test_log_repr() -> None:
    log = getLogger("test_log_repr")
    assert repr(log) == str(log) == "<StructuredLogger for <Logger test_log_repr (WARNING)>>"
    assert repr(log.logger) in repr(log)


@pytest.mark.parametrize("level_method", ["debug", "info", "warning", "error", "exception", "critical"])
def test_stackinfo_last_frame(caplog_all: pytest.LogCaptureFixture, level_method: str) -> None:
    log = getLogger("test_log_level_log")
    log.setLevel(logging.NOTSET)

    getattr(log, level_method)("", stack_info=True)
    stack_info = caplog_all.records[-1].stack_info
    assert stack_info
    stack_info_lines = stack_info.split("\n")

    assert f'File "{Path(__file__)}"' in stack_info_lines[-2]
    assert 'getattr(log, level_method)("", stack_info=True)' in stack_info_lines[-1]

    def call_log() -> None:
        getattr(log, level_method)("", stack_info=True, stacklevel=2)

    call_log()

    stack_info = caplog_all.records[-1].stack_info
    assert stack_info
    stack_info_lines = stack_info.split("\n")

    assert "call_log()" in stack_info_lines[-1]


def test_log_stackinfo_last_frame(caplog_all: pytest.LogCaptureFixture) -> None:
    log = getLogger("test_log_level_log")

    log.log(logging.INFO, "", stack_info=True)

    stack_info = caplog_all.records[-1].stack_info
    assert stack_info
    stack_info_lines = stack_info.split("\n")

    assert f'File "{Path(__file__)}"' in stack_info_lines[-2]
    assert 'log.log(logging.INFO, "", stack_info=True)' in stack_info_lines[-1]

    def call_log() -> None:
        log.log(logging.INFO, "", stack_info=True, stacklevel=2)

    call_log()

    stack_info = caplog_all.records[-1].stack_info
    assert stack_info
    stack_info_lines = stack_info.split("\n")

    assert "call_log()" in stack_info_lines[-1]


@pytest.mark.parametrize(
    "key",
    get_standard_logrecord_keys() - LOGGING_NAMED_ARGS,
)
def test_restricted_keys(key: str, caplog_all: pytest.LogCaptureFixture) -> None:
    """Ensure that log call kwargs keys don't conflict with established LogRecord arg names.

    This doesn't include the few attributes which are also log method arguments, like `msg`.
    """
    log = getLogger("test_restricted_keys")
    val = "some-value"

    log.info("Msg", **{key: val})  # type: ignore[arg-type]
    record = caplog_all.records[-1]
    assert getattr(record, LOG_RECORD_PREFIX + key) == val


@pytest.mark.parametrize(
    ("extra_key", "log_record_attr"),
    [(k, LOG_RECORD_PREFIX + k) for k in get_standard_logrecord_keys()]
    + [(k, k) for k in LOGGING_NAMED_ARGS - get_standard_logrecord_keys()],
)
def test_arguments_via_extra(
    extra_key: str,
    log_record_attr: str,
    caplog_all: pytest.LogCaptureFixture,
) -> None:
    """Test passing keys that conflict with LogRecord attrs or log call args via the extra dict."""
    log = getLogger("test_restricted_keys")
    val = "some-value"

    log.info("Msg", extra={extra_key: val})
    record = caplog_all.records[-1]
    assert getattr(record, log_record_attr) == val
