import time

import logging
import typing
import attr

from abc import ABC, abstractmethod

from strategy_bridge.bus import DataBus


@attr.s(auto_attribs=True, kw_only=True)
class BaseProcessor(ABC):

    processing_pause: typing.Optional[float] = 1
    should_run_infinitely: bool = True
    reduce_pause_on_process_time: bool = False
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
        try:
            if self.should_run_infinitely:
                while True:
                    self.main_loop()
            else:
                self.process()
        except KeyboardInterrupt:
            self.logger.warning(f"Interrupted {self.__class__.__name__}. Finalizing processing")
            self.finalize()

    def main_loop(self):
        before = time.time()
        self.process()
        after = time.time()
        took = after - before
        if self.processing_pause:
            pause = self.processing_pause
            if self.reduce_pause_on_process_time:
                pause -= took
                if pause < 0:
                    self.logger.warning(
                        f"Processor {self.__class__.__name__} took {took:.2f} seconds "
                        f"with expected pause between runs for {self.processing_pause} seconds"
                    )
                    pause = 0
            time.sleep(pause)

    @abstractmethod
    def process(self) -> None:
        pass

    def finalize(self) -> None:
        pass
