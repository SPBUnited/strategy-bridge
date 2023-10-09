import logging

import json

import attr
import websocket
from websocket import WebSocketApp

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
    reconnect_count: int = 5
    should_run_infinitely: bool = False
    records_writer: DataWriter = attr.ib(init=False)
    websocket: WebSocketApp = attr.ib(init=False)

    def initialize(self, data_bus: DataBus) -> None:
        super(BoxFeedbackCollector, self).initialize(data_bus)
        self.records_writer = DataWriter(self.data_bus, config.BOX_FEEDBACK_TOPIC, self.max_records_to_persist)

        self.websocket = websocket.WebSocketApp(
            f"ws://{self.box_ip}:{self.box_port}{self.box_route}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

    def on_open(self, ws):
        pass

    def on_close(self, ws, close_status_code, close_msg):
        pass

    def on_message(self, ws, message):
        parsed_message = json.loads(message)
        self.records_writer.write(parsed_message)

    def on_error(self, ws, error):
        pass

    def finalize(self) -> None:
        self.websocket.close()

    @debugger
    def process(self):
        self.websocket.run_forever(reconnect=self.reconnect_count)
