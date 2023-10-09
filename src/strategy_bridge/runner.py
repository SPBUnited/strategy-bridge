import logging
from multiprocessing import Process

from multiprocessing.managers import BaseManager

import typing

import attr

from strategy_bridge.bus import DataBus
from strategy_bridge.processors import BaseProcessor


class BridgeManager(BaseManager):
    pass


@attr.s(auto_attribs=True, kw_only=True)
class Runner:
    processors: typing.List[BaseProcessor]
    logger: logging.Logger = logging.getLogger(__name__)

    def run(self):
        BridgeManager.register('data_bus', DataBus)
        with BridgeManager() as manager:
            data_bus = manager.data_bus()
            processes = [
                Process(target=self.run_processor, args=(processor, data_bus)) for processor in self.processors
            ]
            for process in processes:
                process.start()
            try:
                for process in processes:
                    process.join()
            except KeyboardInterrupt:
                self.logger.warning("The application was interrupted")

    def run_processor(self, processor: BaseProcessor, data_bus: DataBus) -> None:
        processor.initialize(data_bus)
        processor.run()
