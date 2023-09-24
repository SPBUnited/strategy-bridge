import logging

from datetime import datetime

import time

import typing

from strategy_bridge.bus import Record
from strategy_bridge.common import config
from strategy_bridge.processors import BaseProcessor


logger = logging.getLogger(config.DEBUGGER_LOGGER_NAME)


def record_debugger(func: typing.Callable[..., typing.Any]) -> typing.Callable:
    def wrapper(self: BaseProcessor, record: Record, *args, **kwargs) -> typing.Any:
        assert isinstance(record, Record), "First parameter to decorated function should be of type Record"

        before = time.time()
        result = None
        exception = None
        try:
            result = func(self, record, *args, **kwargs)
        except Exception as e:
            exception = e
        after = time.time()

        msg_start = f"[{self.__class__.__name__}]"
        msg_status = f"[{'Failure' if exception else 'Processed'} after {after - before:.2f} seconds]"
        msg_stats = f"[Delay from input record: {after-record.timestamp:.2f} seconds] " \
                    f"[Input record timestamp: {datetime.fromtimestamp(record.timestamp)}]"
        msg = f"{msg_start} {msg_status} {msg_stats}"
        logger.info(msg)

        if exception:
            raise exception
        return result
    return wrapper
