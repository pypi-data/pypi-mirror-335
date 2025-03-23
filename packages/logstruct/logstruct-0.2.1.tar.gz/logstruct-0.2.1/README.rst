logstruct
=========

Everything you need to turn Python stdlib logging into a proper structured logging library. Rather
than fighting ``logging``, let's live with it.

.. code:: python

    import logging
    import logstruct

    logging.basicConfig(level=logging.INFO)
    logging.root.handlers[0].setFormatter(logstruct.StructuredFormatter())

    log = logstruct.getLogger(__name__)
    log.info("Message with data", key1="val1", data=object())

This prints the following JSON to ``stderr`` that, if pretty-printed, looks as follows:

.. code:: json

    {
      "time": "2025-01-19 09:49:36,489",
      "logger": "__main__",
      "level": "INFO",
      "func": "<module>",
      "line": 8,
      "message": "Message with data",
      "key1": "val1",
      "data": "<object object at 0x765a8a9806f0>"
    }

`Full documentation <https://logstruct.readthedocs.org>`_

Features
--------

- `StructuredLogger <logstruct.StructuredLogger>` - a replacement for `logging.Logger`
  with a simplified interface for adding structured data to logs. (`Usage <logger_usage>`)
- `StructuredFormatter <logstruct.StructuredFormatter>` - a `logging.Formatter`
  implementation that formats log records as JSON. (`Usage <formatter_usage>`)
- `contextual information <context_usage>` to log records with `logstruct.context_scope`.
- Easy to use and simple to configure, **no dependencies**.
- Seamlessly integrates with any code using stdlib `logging`, e.g. Sentry SDK.
- Human readable output for development - see `demo_dev_mode.py <dev_mode_logging>`.

Design principles
-----------------

#. Play well with ``logging``.
#. Be small.

Considerations
--------------

If the standard logging library adds a new kwarg to log methods, e.g. ``logging.Logger.info``, this kwarg,
when passed to ``StructuredLogger``, will be merged into the ``extra`` dict until it is added to
``StructuredLogger`` methods. Using ``StructuredLogger`` is optional.

Logging integrations that rely on monkey-patching ``logging.Formatter.format`` won't see it called because
``StructuredFormatter`` doesn't call this method. Such reliance is extremely unlikely.

Development
-----------

While the project source is dependency-free, `PDM <https://pdm-project.org>`_ is used for management of dev
(testing) and doc (Sphinx/ReadTheDocs) dependencies.

.. code:: sh

    pdm install

You should be able to get away with not using PDM as long as you don't change dependencies.

.. code:: sh

    pip install --editable . -r requirements-dev.txt -r requirements-doc.txt

When dependencies are changed, they need to be locked. This will also write requirements-{dev,doc}.txt.

.. code:: sh

    pdm lock -G :all

Tests are run with pytest and Sphinx’s `doctest` target.

.. code:: sh

   pdm run pytest
   pdm run sphinx-build docs docs/_build -b doctest

``Setuptools-SCM`` and ``build`` are used for building the project. Publishing is done in the CI, using the
old twine method, even though PDM could be used.

British English is used in the project, out of fear of losing my settled status.
