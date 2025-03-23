How it works
============

Components
----------

The following logging and Logstruct components work together to provide a feature-complete
structured logging solution.

* `logstruct.StructuredLogger` - Allows to perform log calls with arbitrary keyword args attached.

    * `logstruct.StructuredFormatterConfig` - Defines all logstruct-specific `StructuredFormatter` configuration.

        * `logstruct.LogField` - Maps LogRecord attributes to key-value pairs 

* `logging.LogRecord` - Contains all data produced by a log call, standard library or logstruct.

* `logging.Logger` - Basic building block of standard library logging topology.

    * `logging.Handler` - Called by loggers provided with handlers (typically the root logger only).

        * `logstruct.StructuredFormatter` - Formats log records as data.

High-level flow
---------------

A standard logging configuration with logstruct enabled works as follows:

1. `logstruct.StructuredLogger` is called by user code

2. `logging.Logger` is called by `logstruct.StructuredLogger`

3. Log propagation according to the configured stdlib logging topology takes place - check `Logging
   Flow`_

4. Final `logging.Logger` is reached (typically ``logging.root``)

5. `logging.Handler` (typically `logging.StreamHandler`) is called by the final logger.

    * `logstruct.StructuredLogger` is called by the handler. It renders a structured log (JSON by
      default) and returns to the handler.

6. The handler outputs the structured log.

This configuration is identical to a typical stdlib logging configuration, except it adds
`logstruct.StructuredLogger` at the beginning and it attaches `logstruct.StructuredFormatter` to
the target log handler.


Detail
------

Calling the logger and producing a LogRecord (points 1-2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Logstruct logger is called with arbitrary keyword arguments. It packages those keyword args in a
dict and passes it as the ``extra`` argument to its underlying standard library logger.

Therefore this code:

.. code:: python

    log = logstruct.getLogger("logger_name")
    log.info("Message", key="value", count=22)

is equivalent to:

.. code:: python

    log = logging.getLogger("logger_name")
    log.info("Message", extra={"key": "value", "count": 22})


In `logging` not all strings are valid ``extra`` dict keys - namely, if LogRecord attributes
are passed in ``extra``, ``KeyError: "Attempt to overwrite '<sth>' in LogRecord"`` is thrown.
In Logstruct this is fixed by prefixing conflicting keys with ``"logstruct_key_"``.


LogRecord propagation (points 3-4)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``LogRecord`` building and propagation happens completely in the standard library logging module.

Once the standard library logger is called with the ``extra`` dictionary carrying the user-supplied
key-vals, this dictionary is merged into ``log_record.__dict__``, creating arbitrary ``LogRecord``
attributes.

The created ``LogRecord`` gets propagated as in the `Logging Flow`_ until it reaches a logger that
handles it by passing it onto a handler configured with a `StructuredFormatter` instance. Typically
this is ``logging.root``.

Handling, formatting, and output (point 5-6)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the ``LogRecord`` is passed onto a logging handler with `StructuredFormatter` attached, the
`StructuredFormatter` processes the ``LogRecord``.

1. It formats the message, timestamp and optional exception info contained in the ``LogRecord``.
   This mutates the ``LogRecord``, which is equivalent to the behaviour of `logging.Formatter`.
2. It picks up standard ``LogRecord`` attributes and places them in a temporary dictionary.
   Attributes can be included, excluded or conditionally included in the produced dictionary. This
   is configured by `LogField` entries in the `StructuredFormatterConfig` struct passed to the
   `StructuredFormatter`.
3. The temp dictionary is updated with the current Logstruct `context <context_usage>` dict.
4. The temp dictionary is updated with non-default ``LogRecord`` attributes.

   Those attributes come from the arbitrary keyword args or the explicit ``extra`` arg originally
   passed in the `StructuredLogger` call. Either way, the kwargs and extras get flattened and
   passed to `logging.Logger`. After the `logging` machinery creates a `logging.LogRecord`, it
   merges them into the log record's attributes.

   Another annoyance is that not all keys can be merged into `logging.LogRecord` attributes, which
   is we compensated for in step 1 by prefixing conflicting keys. Now we have undo it.

   This step solves the confusion introduced by the stdlib ``logging`` library's way of handling the
   ``extra`` dictionary.
5. The temp dictionary is serialised as JSON or some other format, depending on the
   `StructuredFormatterConfig.dumps_fn` attribute.

This completes the process of turning ``logging`` into a complete structured logging library.

.. _Logging Flow: https://docs.python.org/3/howto/logging.html#logging-flow
