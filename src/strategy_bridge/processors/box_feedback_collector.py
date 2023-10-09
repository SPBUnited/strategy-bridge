import json

import attr
import websocket
from websocket import WebSocket

from strategy_bridge.bus import DataWriter, DataBus
from strategy_bridge.common import config
from strategy_bridge.processors import BaseProcessor
from strategy_bridge.utils.debugger import debugger


@attr.s(auto_attribs=True)
class BoxFeedbackCollector(BaseProcessor):

    processing_pause = 0.01
    max_records_to_persist: int = 30
    box_ip: str = "10.0.120.103"
    box_port: int = 8001
    box_route: str = "/api/webclient"
    records_writer: DataWriter = attr.ib(init=False)
    websocket: WebSocket = attr.ib(init=False)

    def initialize(self, data_bus: DataBus) -> None:
        super(BoxFeedbackCollector, self).initialize(data_bus)
        self.records_writer = DataWriter(self.data_bus, config.BOX_FEEDBACK_TOPIC, self.max_records_to_persist)
        self.websocket = websocket.create_connection(f"ws://{self.box_ip}:{self.box_port}{self.box_route}")

    @debugger
    def process(self):
        message = self.websocket.recv()
        if not message:
            return
        parsed_message = json.loads(message)
        self.records_writer.write(parsed_message)
