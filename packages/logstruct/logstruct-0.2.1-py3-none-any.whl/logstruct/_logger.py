"""A custom logger that makes extra kwargs available as the extra dict."""

from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
from types import TracebackType
from typing import Optional, Union

from logstruct._constants import LOG_RECORD_PREFIX, get_standard_logrecord_keys

# Taken from the official Python typeshed, TypeAlias removed so there's no dependency on typing_extensions.
_ArgsType = Union[tuple[object, ...], Mapping[str, object]]
_SysExcInfoType = Optional[
    Union[
        bool,
        Union[tuple[type[BaseException], BaseException, Optional[TracebackType]], tuple[None, None, None]],
        BaseException,
        None,
    ]
]
_ExcInfoType = Union[None, bool, _SysExcInfoType, BaseException]


class StructuredLogger:
    """A structured logger forwarding log calls to an underlying stdlib logger with the same name.

    The core difference over the stdlib is passing kwargs as the ``extra`` dict. It isn't necessary to use
    this class to make use of the structured formatter.

    Not all methods are proxied. Use the :attr:`StructuredLogger.logger` attribute to reach the stdlib logger.

    .. automethod:: __init__
    """

    logger: logging.Logger
    """Underlying stdlib logger."""

    def __init__(self, name: str | None) -> None:
        """Initialise the underlying stdlib logger.

        :param name: Underlying stdlib logger name, ``None`` means the root logger.
        """
        self.logger = logging.getLogger(name)

    @property
    def name(self) -> str:
        """Get the name of the underlying logger."""
        return self.logger.name

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the underlying logger."""
        self.logger.name = name

    @property
    def level(self) -> int:
        """Get the log level of the underlying logger."""
        return self.logger.level

    def setLevel(self, level: int) -> None:
        """Set log level of the underlying logger."""
        self.logger.setLevel(level)

    def getEffectiveLevel(self) -> int:
        """Get the effective log level of the underlying logger."""
        return self.logger.getEffectiveLevel()

    def isEnabledFor(self, level: int) -> bool:
        """Check if the underlying logger is enabled for this method."""
        return self.logger.isEnabledFor(level)

    @property
    def parent(self) -> logging.Logger | None:
        """Get the parent of the underlying stdlib logger."""
        return self.logger.parent

    @parent.setter
    def parent(self, value: logging.Logger | None) -> None:
        """Set the parent of the underlying stdlib logger."""
        self.logger.parent = value

    @property
    def handlers(self) -> list[logging.Handler]:
        """Get handlers of the underlying stdlib logger."""
        return self.logger.handlers

    @handlers.setter
    def handlers(self, value: list[logging.Handler]) -> None:
        """Set handlers of the underlying stdlib logger."""
        self.logger.handlers = value

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Delegate a debug call to the underlying logger, merging leftover kwargs into ``extra``."""
        if self.isEnabledFor(logging.DEBUG):
            self.log(
                logging.DEBUG,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel + 1,
                extra=extra,
                **kwargs,
            )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Delegate a info call to the underlying logger, merging leftover kwargs into ``extra``."""
        if self.isEnabledFor(logging.INFO):
            self.log(
                logging.INFO,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel + 1,
                extra=extra,
                **kwargs,
            )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Delegate a warning call to the underlying logger, merging leftover kwargs into ``extra``."""
        if self.isEnabledFor(logging.WARNING):
            self.log(
                logging.WARNING,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel + 1,
                extra=extra,
                **kwargs,
            )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Delegate an error call to the underlying logger, merging leftover kwargs into ``extra``."""
        if self.isEnabledFor(logging.ERROR):
            self.log(
                logging.ERROR,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel + 1,
                extra=extra,
                **kwargs,
            )

    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = True,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Call `error` with exc_info=True."""
        self.error(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            extra=extra,
            **kwargs,
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Delegate a critical call to the underlying logger, merging leftover kwargs into ``extra``."""
        if self.isEnabledFor(logging.CRITICAL):
            self.log(
                logging.CRITICAL,
                msg,
                *args,
                exc_info=exc_info,
                stack_info=stack_info,
                stacklevel=stacklevel + 1,
                extra=extra,
                **kwargs,
            )

    def log(
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
        **kwargs: object,
    ) -> None:
        """Delegate a log call to the underlying logger, merging leftover kwargs into ``extra``."""
        if not self.isEnabledFor(level):
            return

        # Sadly, `extra` keys get associated with LogRecord as attributes, causing certain reserved
        # keys like "name" (or anything else in `get_standard_logrecord_keys()`) throw KeyErrors.
        #
        # We're fixing it here.
        #
        # It would be much easier to pass extras and kwargs as a dict or 2 separate dicts but that
        # would not play well with tools that read extras the usual way.
        need_escaping = get_standard_logrecord_keys()

        if extra is None:
            assignable_extra = {}
        else:
            assignable_extra = {
                (k if k not in need_escaping else LOG_RECORD_PREFIX + k): v for k, v in extra.items()
            }

        for k, v in kwargs.items():
            assignable_extra[k if k not in need_escaping else LOG_RECORD_PREFIX + k] = v

        if sys.version_info >= (3, 11):
            stacklevel += 1

        return self.logger._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=assignable_extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    def __repr__(self) -> str:
        """Representation including the underlying stdlib logger."""
        return f"<{self.__class__.__name__} for {self.logger!r}>"


# Stdlib logging has a thing called a Manager which "holds the hierarchy of loggers". Under normal
# curcumstances there's only one manager, and I don't think any app has ever made use of more than one.
# That's why the name to StructuredLogger mapping is so basic here.
_LOGGERS: dict[str | None, StructuredLogger] = {}


def getLogger(name: str | None) -> StructuredLogger:
    """Retrieve or get a StructuredLogger instance.

    ``getLogger(None)`` will produce a StructuredLogger delegating to the root logger.
    """
    return _LOGGERS.setdefault(name, StructuredLogger(name))
