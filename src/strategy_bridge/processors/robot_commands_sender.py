import attr
import zmq

from strategy_bridge.bus import DataReader, DataBus
from strategy_bridge.common import config
from strategy_bridge.processors import BaseProcessor
from strategy_bridge.utils.debugger import debugger


@attr.s(auto_attribs=True)
class RobotCommandsSender(BaseProcessor):

    commands_reader: DataReader = attr.ib(init=False)

    def initialize(self, data_bus: DataBus) -> None:
        super(RobotCommandsSender, self).initialize(data_bus)

        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{config.COMMANDS_PUBLISH_PORT}")

        self.commands_reader = DataReader(self.data_bus, config.ROBOT_COMMANDS_TOPIC)

    @debugger
    def process(self):
        commands = self.commands_reader.read_new()
        for command in commands:
            self.socket.send(command.content)
