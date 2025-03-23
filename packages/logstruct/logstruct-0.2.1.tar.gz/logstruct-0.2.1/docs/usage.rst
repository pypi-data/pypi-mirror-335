Usage
=====

..
    WARNING! The program-output directive caches the output based on the command. `make clean` is needed when
    demos change to see the changes locally.

    Also, sphinx-doctest runs all tests in the `builtins` module... This affects the logger name if
    we pass `__name__`.


Setup
-----

``StructuredLogger``
^^^^^^^^^^^^^^^^^^^^

No special setup is needed for `StructuredLogger <logstruct.StructuredLogger>`. Just call
`logstruct.getLogger` to obtain it and use it.

All key `logging.Logger` methods exist in `StructuredLogger`. For the ones that don't, use the
public `StructuredLogger.logger <StructuredLogger.logger>` attribute to manage the stdlib logger.

``StructuredFormatter``
^^^^^^^^^^^^^^^^^^^^^^^

In order to format incoming log records as JSON, `StructuredFormatter
<logstruct.StructuredFormatter>` needs to be assigned to the `log handler <logging.Handler>` in use.
Once this is done, log records will be output as JSON, regardless of where they come from -
`logging.Logger` or `StructuredLogger <logstruct.StructuredLogger>`.

.. testsetup::

   import sys
   import logging
   import logstruct

   # Use sys.stdout so that doctests capture the logs
   logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

.. testcode::

   logging.basicConfig(level=logging.DEBUG)
   logging.root.handlers[0].setFormatter(logstruct.StructuredFormatter())

   logging.getLogger("stdlib-logger").info("hello world")

.. testoutput::

   {"time": "...", "logger": "stdlib-logger", "level": "INFO", ..., "message": "hello world"}

``StructuredFormatter`` supports the standard `dictConfig method <dict_config_file>` and the legacy
`fileConfig method <logging_config_file>` of **file configuration**.


.. _logger_usage:

Structured data
---------------

`StructuredLogger <logstruct.StructuredLogger>`'s logging API is nearly identical to the standard
library `logging.Logger`. The key difference is that additional **keyword arguments** provided to
logging functions are automatically **included in structured output**.

.. testcode::

   logger = logstruct.getLogger(__name__)
   logger.info("hello", request_id=1234, user="black_knight")

.. testoutput::

   {..., "level": "INFO", ..., "message": "hello", "request_id": 1234, "user": "black_knight"}

This works for all logging levels.

.. testcode::
   :hide:

   logger.setLevel(logging.DEBUG)

.. testcode::

   logger.debug("good to know", request_id=1234)
   logger.info("doing this and that", request_id=1234)
   logger.warning("take a look", request_id=1234)
   logger.error("uh-oh", request_id=1234)
   logger.critical("abort", request_id=1234)

.. testoutput::

   {..., "level": "DEBUG", ..., "message": "good to know", "request_id": 1234}
   {..., "level": "INFO", ..., "message": "doing this and that", "request_id": 1234}
   {..., "level": "WARNING", ..., "message": "take a look", "request_id": 1234}
   {..., "level": "ERROR", ..., "message": "uh-oh", "request_id": 1234}
   {..., "level": "CRITICAL", ..., "message": "abort", "request_id": 1234}

Alternatively, structured data can be passed as a dictionary in the ``extra`` parameter:

.. testcode::

   logger.info("hello", extra={"request_id": 1234, "user": "black_knight"})

.. testoutput::

   {..., "message": "hello", "request_id": 1234, "user": "black_knight"}

Passing data in the ``extra`` parameter also works for **standard library loggers**:

.. testcode::

   standard_logger = logging.getLogger("stdlib-logger")
   standard_logger.info("hello", extra={"request_id": 1234})

.. testoutput::

   {..., "message": "hello", "request_id": 1234}


Structured data from dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It may be tempting to unpack a dictionary like this:

.. code:: python

    data = {k: v, ...}
    log.info("hello", **data)

This will not typecheck correctly due to the inclusion of stdlib arguments like ``stack_level`` in log
method signatures.

This, however, will typecheck:

.. code:: python

    log.info("hello", extra=data)


Exception logging
^^^^^^^^^^^^^^^^^

Similar to `logging.Logger <logging.Logger.debug>`, you can include exception information using the ``exc_info`` parameter:

.. testcode::

   logger.error("uh-oh", exc_info=ValueError("wrong value"), request_id=1234)

.. testoutput::

   {..., "message": "uh-oh", "exc_text": "ValueError: wrong value", "request_id": 1234}

The currently handled exception is automatically captured if ``exc_info`` is true or if
`logger.exception <logstruct.StructuredLogger.exception>` is called.

.. testcode::

   try:
       x = 1 / 0
   except ZeroDivisionError:
       logger.debug("debug", exc_info=True, request_id=1234)
       logger.exception("error", request_id=1234)

.. testoutput::

   {..., "level": "DEBUG",... "message": "debug", "exc_text": "Traceback ...ZeroDivisionError: division by zero", "request_id": 1234}
   {..., "level": "ERROR",... "message": "error", "exc_text": "Traceback ...ZeroDivisionError: division by zero", "request_id": 1234}

``exc_text`` includes the traceback of the exception relative to the logging call. You can customise
exception formatting by subclassing `StructuredFormatter` and overriding
`logging.Formatter.formatException`, just like you would do it with any other `logging.Formatter`.

Stack logging
^^^^^^^^^^^^^

Similar to `logging.Logger <logging.Logger.debug>`, you can include stack information using the ``stack_info`` parameter:

.. testcode::

   logger.info("with stack", stack_info=True, stacklevel=0)

.. testoutput::

   {..., "stack_info": "Stack (most recent call last):...", ...}

The ``stacklevel`` parameter controls the number of stack frames that are omitted from
``stack_info``, relative to the frame from which the log method is called.


.. _context_usage:

Context variables
-----------------

Logstruct context variables are meant to contain data relevant to the current operation, like
message ID, request path, user ID, job name, job ID, etc. Once set, they are shared by all
subsequent logs until they are unset.

Context variables are automatically incorporated in produced structured logs but they can be overridden by
keyword args directly passed to log calls. Context variables are implemented with `contextvars.Context`
which makes them local to the current thread, asyncio task, or gevent task. Context variables are automatically inherited by child tasks but not by spawned threads.

.. testcleanup::

   logstruct.clear_scope()

You can use `context_scope <logstruct.context_scope>` to add contextual information to all log
records within the scope.

.. testcode::

   with logstruct.context_scope(request_id="1234"):
       logger.info("has context", user="abc")

   logger.info("scope ended")

.. testoutput::

   {..., "message": "has context", "request_id": "1234", "user": "abc"}
   {..., "message": "scope ended"}

Contexts can be nested. Inner scopes shadow data from outer scopes.

.. testcode::

   with logstruct.context_scope(outer="outer", redefined="outer"):
       with logstruct.context_scope(inner="inner", redefined="inner"):
           logger.info("inner context")

.. testoutput::

   {..., "message": "inner context", "inner": "inner", "redefined": "inner", "outer": "outer"}


You can modify the current context with `add_context <logstruct.add_context>`, `remove_context
<logstruct.remove_context>`, or `clear_scope <logstruct.clear_scope>`.

.. testcode::

   logstruct.add_context(request_id="1234", user="abc")
   logger.info("has context")

   logstruct.remove_context("user")
   logger.info("only request_id")

   logstruct.clear_scope()
   logger.info("no context")

.. testoutput::

   {..., "message": "has context", "request_id": "1234", "user": "abc"}
   {..., "message": "only request_id", "request_id": "1234"}
   {..., "message": "no context"}

Modifications only apply to the current scope. Once the scope ends, all
modifications are lost.

.. testcode::

   with logstruct.context_scope(request_id="1234"):
     logstruct.add_context(user="abc")
     logger.info("modified")

   logger.info("unmodified")

.. testoutput::

   {..., "message": "modified", "request_id": "1234", "user": "abc"}
   {..., "message": "unmodified"}

Configuration
-------------

.. _logger_config:

Logger configuration
^^^^^^^^^^^^^^^^^^^^

There is no configuration specific to `StructuredLogger`. Since each `StructuredLogger` is paired
with a `logging.Logger` with the same name, that logger should be configured as in the `official
docs <https://docs.python.org/3/library/logging.config.html#module-logging.config>`_.

`logging.config.fileConfig` and `logging.config.dictConfig` configuration works just like it does in
the standard library.

.. _formatter_usage:

Formatter configuration
^^^^^^^^^^^^^^^^^^^^^^^

A `StructuredFormatter` is configured using `StructuredFormatterConfig`.

Logstruct provides two default configs: `logstruct.CONFIG_FORMATTED_MESSAGE` and
`logstruct.CONFIG_RAW_MESSAGE`, which can be used directly or copied to derive custom configuration.

.. list-table:: `StructuredFormatterConfig` attributes
    :header-rows: 1

    *   - Attribute
        - Default
        - Description

    *   - `format_message <StructuredFormatterConfig.format_message>`
        - ``True``
        - Controls whether log messages should be
          formatted with positional log call arguments (using ``record.getMessage()``) or left unformatted
          (keeping ``record.msg``).

    *   - `uses_time <StructuredFormatterConfig.uses_time>`
        - ``True``
        - Determines if the current time should be assigned to ``LogRecord.asctime``.

    *   - `log_fields <StructuredFormatterConfig.log_fields>`
        - `DEFAULT_LOG_FIELDS`
        - Defines how LogRecord attributes map to output key-value pairs.  See `Log field
          configuration <log_field_configuration>` below.

    *   - `get_context_fn <StructuredFormatterConfig.get_context_fn>`
        - `logstruct.get_context`
        - Function to retrieve `context variables <context_usage>` that get merged into the output.

    *   - `dumps_fn <StructuredFormatterConfig.dumps_fn>`
        - `json.dumps` with ``default=repr``
        - Function used to serialise final structured into text for logging.


.. _log_field_configuration:

Log field configuration
^^^^^^^^^^^^^^^^^^^^^^^

The ``LogField`` struct allows you to map `logging.LogRecord` attributes to structured output keys.
``LogRecord`` is the piece of log data sent from the logger to the handler to be formatted by its
formatter and written out. ``LogRecord`` attribute reference can be found in `standard library docs
<https://docs.python.org/3/library/logging.html#logrecord-attributes>`_.

.. list-table:: `LogField` attributes
    :header-rows: 1

    *   - Attribute
        - Default?
        - Description

    *   - `LogField.source`

          (or legacy ``log_record_attr``)
        - *required*
        - Source LogRecord attribute name or a callable that receives a LogRecord and returns a
          string.

    *   - `LogField.dest`

          (or legacy ``struct_key``)
        - *required*
        - The output key in the structured log.

    *   - `LogField.condition`
        - ``None``
        - An optional callable to determine if the field should be included. Always included
          if ``None``.

For example, this ``LogField`` will try to pick up the ``taskName`` attribute from the ``LogRecord``
and include it as the ``"task"`` key in the produced log. If the attribute is missing, the key won't
be included.

.. code:: python

    LogField("taskName", "task", bool),

.. code:: json

    {"task": "Task-1234"}


If the condition is missing, the key will always be included even if the source ``LogRecord``
attribute is missing or evaluates to False.

.. code:: python

    LogField("taskName", "task"),


.. code:: json

    {"task": null}


Highly customised configuration example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following example defines completely custom configuration, featuring:

- disabling log message formatting

- specifying own ``LogFields``

- custom serialisation function

The example configures Logstruct in Python - see `Using configuration files <config_files>` for
config file examples.

.. literalinclude:: ../demo_custom.py
   :language: py

.. program-output::  ../demo_custom.py
   :caption: log output

.. _config_files:

Using configuration files
-------------------------

File configuration of `StructuredFormatter` is fully supported, including configuring `LogFields
<dict_config_log_fields>`.

.. _dict_config_file:

Basic ``dictConfig``
^^^^^^^^^^^^^^^^^^^^

You can configure ``logstruct`` with a data file by loading it and passing it to
`logging.config.dictConfig`.

.. literalinclude:: ../example_config.yaml
   :caption: example_config.yaml
   :language: yaml

.. testsetup:: dict_config

   import logging.config
   from pathlib import Path
   import yaml
   import logstruct
   import sys

   # Hack to make doctest see the logs.
   real_stderr = sys.stderr
   sys.stderr = sys.stdout

.. testcleanup:: dict_config

    sys.stderr = real_stderr

.. testcode:: dict_config

   config = yaml.safe_load(Path("example_config.yaml").read_text())
   logging.config.dictConfig(config)
   logger = logstruct.getLogger(__name__)
   logger.info("hello", request_id=1234)

.. testoutput:: dict_config

   {"time": "...", "level": "INFO", ..., "message": "hello", "request_id": 1234}


``StructuredFormatter`` config in ``dictConfig``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Formatter configuration is available thanks to the ``()`` feature in ``dictConfig``, allowing to
pass custom parameters to the formatter's constructor.

.. literalinclude:: ../example_config_advanced.yaml
   :caption: example_config.yaml
   :language: yaml
   :start-at: formatters:
   :end-at: uses_time

Refer to `Advanced dictConfig example <advanced_dict_config>` for complete code.

Callables in ``dictConfig``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some values, for example `StructuredFormatterConfig.dumps_fn`, are callables. While it isn't
possible to define functions in config files, config attributes can still reference Python
functions. For example, if ``user_module.submodule.user_func`` is passed as a value of a callable
config field, the ``user_module.submodule`` module will be imported and ``user_func`` will be
retrieved from it.

.. literalinclude:: ../example_config_advanced.yaml
   :caption: example_config.yaml
   :language: yaml
   :lines: 10-13,37

.. _dict_config_log_fields:

LogFields in ``dictConfig``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is also possible to configure `LogFields <StructuredFormatterConfig.log_fields>` via ``dictConfig``.

.. literalinclude:: ../example_config_advanced.yaml
   :caption: example_config.yaml
   :language: yaml
   :lines: 10-13,16-21
   :append: ... etc ...

.. note::

    ``LogField.source`` can be either a string or a callable and the two are distinguished by the presence
    of a dot in the value, so:

    - ``source: lineno`` will be the ``LogRecord.lineno`` attribute

    - ``source: my_module.get_line_no`` will be the ``get_line_no`` function in ``my_module``.

    If for whatever reason you want your ``source`` callable to be a built-in, you need to spell out the
    ``__builtins__`` module explicitly, e.g. ``source: __builtins__.vars``

.. _advanced_dict_config:

Advanced ``dictConfig`` example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following example uses a YAML file to define data passed to `logging.config.dictConfig` and
specify custom `StructuredFormatterConfig`, including log fields. Callables are referenced from the
``dumps_fn`` and a number of ``condition`` keys. No Python code is used to specify configuration.

.. literalinclude:: ../example_config_advanced.yaml
   :caption: example_config.yaml
   :language: yaml

.. testsetup:: dict_config_advanced

   import logging.config
   from pathlib import Path
   import yaml
   import logstruct
   import sys

   # Hack to make doctest see the logs.
   real_stderr = sys.stderr
   sys.stderr = sys.stdout

.. testcleanup:: dict_config_advanced

    sys.stderr = real_stderr

.. testcode:: dict_config_advanced

   config = yaml.safe_load(Path("example_config_advanced.yaml").read_text())
   logging.config.dictConfig(config)
   logger = logstruct.getLogger(__name__)
   logger.info("hello", request_id=1234)

.. testoutput:: dict_config_advanced

    {"ts": "...", "level": "INFO", "logger": "...", "line": ..., "msg": "hello", "request_id": 1234}

.. note::

    Sadly, YAML sucks. It is used here only because Python uses it in its `dictConfig
    <logging.config.dictConfig>` documentation.

.. _logging_config_file:

Legacy ``fileConfig`` (ini files)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``logstruct`` can be configured with the standard library's configuration file format and the
`fileConfig <logging.config.fileConfig>` function. Unlike `dictConfig <dict_config_log_fields>`,
this method doesn't allow for custom formatter configuration.

.. literalinclude:: ../example_config.ini
   :caption: example_config.ini
   :language: ini

.. testsetup:: file_config

   import logging.config
   from logstruct import getLogger
   import sys

   real_stderr = sys.stderr
   sys.stderr = sys.stdout

.. testcleanup:: file_config

   sys.stderr = real_stderr

.. testcode:: file_config

   logging.config.fileConfig("example_config.ini", disable_existing_loggers=False)
   logger = getLogger(__name__)
   logger.info("hello", request_id=1234)

.. testoutput:: file_config

   {"time": "...", "level": "INFO", ..., "message": "hello", "request_id": 1234}


.. _dev_mode_logging:

Development mode logging
------------------------

In this demo the ``DEBUG`` env var set to a non-empty value makes logs formatted in a developer-friendly way,
but unlike the default formatter, will include the ``extra`` dictionary, where our log call key-values go.

.. literalinclude:: ../demo_dev_mode.py
   :language: py

.. program-output:: sh -c 'DEBUG=1 ../demo_dev_mode.py'
   :caption: DEBUG=1

.. program-output:: ../demo_dev_mode.py
   :caption: DEBUG not set
   :shell:
