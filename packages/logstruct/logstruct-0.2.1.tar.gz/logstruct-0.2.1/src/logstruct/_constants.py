import functools
import logging

LOG_RECORD_PREFIX = "logstruct_key_"


@functools.cache
def get_standard_logrecord_keys() -> set[str]:
    return set(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime"}


@functools.cache
def get_prefixed_standard_logrecord_keys() -> set[str]:
    return {LOG_RECORD_PREFIX + k for k in get_standard_logrecord_keys()}
