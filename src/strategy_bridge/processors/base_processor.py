import time

import logging
import typing
import attr

from abc import ABC, abstractmethod

from strategy_bridge.bus import DataBus


@attr.s(auto_attribs=True, kw_only=True)
class BaseProcessor(ABC):

    processing_pause: typing.Optional[float] = 1
    should_debug: bool = False
    logger: logging.Logger = logging.getLogger(__name__)
    data_bus: DataBus = attr.ib(init=False)
    is_initialized: bool = attr.ib(init=False, default=False)

    def initialize(self, data_bus: DataBus) -> None:
        self.data_bus = data_bus
        self.is_initialized = True

    def run(self) -> None:
        if not self.is_initialized:
            raise Exception("Processor should be initialized first")
        self.logger.info(f"Running processor: {self.__class__.__name__}")
        while True:
            try:
                self.process()
                if self.processing_pause:
                    time.sleep(self.processing_pause)
            except KeyboardInterrupt:
                self.logger.warning(f"Interrupted {self.__class__.__name__}. Finalizing processing")
                self.finalize()

    @abstractmethod
    def process(self) -> None:
        pass

    def finalize(self) -> None:
        pass
