Changelog
=========

Upcoming
--------

...

v0.2.1 2025-03-22
-----------------

* Working around `logging`'s limitation of permitted ``extra`` dict keys.

  In `logging`, passing ``extra`` keys that conflict with `logging.LogRecord` attributes results in
  a `KeyError` raised. We work around this problem by prefixing those keys with
  ``"logstruct_key_"``.

  The sane alternative of passing structured data in a separate dict, rather than merging them into
  the LogRecord, is not taken, since 3rd party tooling will expect the standard, insane way.


v0.2.0 2025-03-02
-----------------

* Many documentation improvements.

* Ability to configure `StructuredFormatter` using `dictConfig <advanced_dict_config>`.

* `StructuredFormatter`: support for the ``default`` argument.

* Rename of `LogField` attributes: ``log_record_attr`` → ``source``, ``struct_key`` → ``dest``.

  Old names supported as constructor kwargs until 1.0.

* `LogField.source`, other than a ``LogRecord`` attribute name, can now be a callable producing a
  value from ``LogRecord``.

* Fix stack info for `StructuredLogger.log`.

  Before, ``log.info("", stack_info=True)`` would skip the frame where the log method was called.


v0.1.1 2025-01-24
-----------------

* Calling `StructuredLogger.exception` with an exception as ``exc_info`` will include the exception
  in the log instead of ``NoneType: None``. (`#1`_)

.. _#1: https://gitlab.com/karolinepauls/logstruct/-/issues/1

v0.1 2024-08-08
---------------

Initial release

* `logstruct.StructuredLogger`
* `logstruct.StructuredFormatter`
* Context: `logstruct.context_scope`, `logstruct.add_context`, `logstruct.remove_context`, etc.