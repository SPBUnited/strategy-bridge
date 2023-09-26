import typing

import attr

from strategy_bridge.bus import Record, DataBus


@attr.s(auto_attribs=True)
class DataReader:

    data_bus: DataBus
    read_topic_name: str
    last_read_message_timestamp: float = 0

    def read_new(self) -> typing.List[Record]:
        records = self.data_bus.read_from_timestamp(self.read_topic_name, self.last_read_message_timestamp)
        if records:
            self.last_read_message_timestamp = records[-1].timestamp
        return records

    def read_all(self) -> typing.List[Record]:
        return self.data_bus.read_all(self.read_topic_name)
