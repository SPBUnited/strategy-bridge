import logging

from datetime import datetime

import time

import typing

from strategy_bridge.bus import Record
from strategy_bridge.common import config
if typing.TYPE_CHECKING:
    from strategy_bridge.processors import BaseProcessor


logger = logging.getLogger(config.DEBUGGER_LOGGER_NAME)


def wrap_with_measurements(self: "BaseProcessor", func: typing.Callable[..., typing.Any], *args, **kwargs):
    before = time.time()
    result = None
    exception = None
    try:
        result = func(self, *args, **kwargs)
    except Exception as e:
        exception = e
    after = time.time()
    return before, after, result, exception


def debugger(func: typing.Callable[..., typing.Any]) -> typing.Callable:
    def wrapper(self: "BaseProcessor", *args, **kwargs) -> typing.Any:
        if self.should_debug:
            before, after, result, exception = wrap_with_measurements(self, func, *args, **kwargs)
            logger.info(f"[{self.__class__.__name__}] [Processing took {after - before:.2f} seconds] "
                        f"[Current timestamp: {datetime.fromtimestamp(after)}]")

            if exception:
                raise exception
            return result
        else:
            return func(self, *args, **kwargs)
    return wrapper


def record_debugger(func: typing.Callable[..., typing.Any]) -> typing.Callable:
    def wrapper(self: "BaseProcessor", record: Record, *args, **kwargs) -> typing.Any:
        assert isinstance(record, Record), "First parameter to decorated function should be of type Record"

        before, after, result, exception = wrap_with_measurements(self, func, record, *args, **kwargs)

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
