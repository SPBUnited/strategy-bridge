import attr

from strategy_bridge.bus import DataWriter, DataBus
from strategy_bridge.common import config
from strategy_bridge.processors import BaseProcessor
from strategy_bridge.larcmacs.receiver import ZmqReceiver
from strategy_bridge.utils.debugger import debugger


@attr.s(auto_attribs=True)
class VisionDetectionsCollector(BaseProcessor):

    max_records_to_persist: int = 30
    records_writer: DataWriter = attr.ib(init=False)
    receiver: ZmqReceiver = attr.ib(init=False)

    def initialize(self, data_bus: DataBus) -> None:
        super(VisionDetectionsCollector, self).initialize(data_bus)
        self.records_writer = DataWriter(self.data_bus, config.VISION_DETECTIONS_TOPIC, self.max_records_to_persist)
        self.receiver = ZmqReceiver(port=config.VISION_DETECTIONS_SUBSCRIBE_PORT)

    @debugger
    def process(self):
        message = self.receiver.next_message()
        if not message:
            return
        self.records_writer.write(message)
