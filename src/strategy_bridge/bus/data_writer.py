import time

import typing

import attr

from strategy_bridge.bus import Record, DataBus


@attr.s(auto_attribs=True)
class DataWriter:

    data_bus: DataBus
    write_topic_name: str
    max_persisted_records_count: int

    def __attrs_post_init__(self):
        self.data_bus.register_topic(self.write_topic_name, self.max_persisted_records_count)

    def write(self, content: typing.Any):
        record = Record(content, time.time())
        self.data_bus.write(self.write_topic_name, record)
