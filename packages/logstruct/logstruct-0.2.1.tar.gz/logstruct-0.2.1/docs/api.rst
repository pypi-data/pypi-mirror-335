API Reference
=============

Logging
-------

.. autofunction:: logstruct.getLogger

.. autoclass:: logstruct.StructuredLogger
   :member-order: bysource

Context
-------

.. autofunction:: logstruct.context_scope

.. autofunction:: logstruct.add_context

.. autofunction:: logstruct.remove_context

.. autofunction:: logstruct.clear_scope

.. autofunction:: logstruct.get_context

Formatting
----------

.. autoclass:: logstruct.StructuredFormatter
   :member-order: bysource

.. autoclass:: logstruct.StructuredFormatterConfig
   :member-order: bysource

.. autoclass:: logstruct.LogField
   :member-order: bysource

.. autofunction:: logstruct.make_friendly_dump_fn

.. data:: logstruct.CONFIG_FORMATTED_MESSAGE

Default configuration that includes most relevant ``LogRecord`` fields in produced "structured"
logs.

.. code:: python

    logstruct.StructuredFormatterConfig(
        format_message=True,
        uses_time=True,
        log_fields=(
            logstruct.LogField(source="asctime", dest="time", condition=bool),
            logstruct.LogField(source="name", dest="logger", condition=None),
            logstruct.LogField(source="levelname", dest="level", condition=None),
            logstruct.LogField(source="funcName", dest="func", condition=None),
            logstruct.LogField(source="lineno", dest="line", condition=None),
            logstruct.LogField(source="message", dest="message", condition=None),
            logstruct.LogField(source="exc_text", dest="exc_text", condition=bool),
            logstruct.LogField(source="stack_info", dest="stack_info", condition=bool),
        ),
        get_context_fn=logstruct.get_context,
        dumps_fn=functools.partial(json.dumps, default=repr),
    )

.. data:: logstruct.CONFIG_RAW_MESSAGE

A variant of the default config that preserves the raw message and adds an extra
``"positional_args"`` key.

.. code:: python

    logstruct.StructuredFormatterConfig(
        format_message=False,
        uses_time=True,
        log_fields=(
            logstruct.LogField(source="asctime", dest="time", condition=bool),
            logstruct.LogField(source="name", dest="logger", condition=None),
            logstruct.LogField(source="levelname", dest="level", condition=None),
            logstruct.LogField(source="funcName", dest="func", condition=None),
            logstruct.LogField(source="lineno", dest="line", condition=None),
            logstruct.LogField(source="message", dest="message", condition=None),
            logstruct.LogField(source="exc_text", dest="exc_text", condition=bool),
            logstruct.LogField(source="stack_info", dest="stack_info", condition=bool),
            logstruct.LogField(source="args", dest="positional_args", condition=bool),
        ),
        get_context_fn=logstruct.get_context,
        dumps_fn=functools.partial(json.dumps, default=repr),
    )

.. data:: logstruct.DEFAULT_DUMPS_FN

.. code:: python

    functools.partial(json.dumps, default=repr)

.. data:: logstruct.DEFAULT_LOG_FIELDS

``log_fields`` used in `CONFIG_FORMATTED_MESSAGE`.

.. code:: python

    (
        logstruct.LogField(source="asctime", dest="time", condition=bool),
        logstruct.LogField(source="name", dest="logger", condition=None),
        logstruct.LogField(source="levelname", dest="level", condition=None),
        logstruct.LogField(source="funcName", dest="func", condition=None),
        logstruct.LogField(source="lineno", dest="line", condition=None),
        logstruct.LogField(source="message", dest="message", condition=None),
        logstruct.LogField(source="exc_text", dest="exc_text", condition=bool),
        logstruct.LogField(source="stack_info", dest="stack_info", condition=bool),
    )
