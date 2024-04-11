import logging
import threading
import traceback
from typing import Any, Callable, TypeAlias

QueryArgs: TypeAlias = dict[str, Any]
QuerySet: TypeAlias = list[QueryArgs]


DEFAULT_LOG_FORMATTER = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(DEFAULT_LOG_FORMATTER)


class Thread(threading.Thread):

    def __init__(
        self,
        name: str | None = None,
        fargs=(),
        fkwargs=None,
        *,
        daemon: bool | None = None,
        log_level: int = logging.INFO,
        active: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(name=name, args=fargs, kwargs=kwargs, daemon=daemon)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.addHandler(STREAM_HANDLER)

        self.RUNNING = active

    def __str__(self) -> str:
        return self.name

    def set_log_level(self, log_level: int):
        self.logger.setLevel(log_level)

    def execute(self):
        raise NotImplementedError(
            "Must implement the execute function to run the thread."
        )

    def kill(self, *args):
        """
        Kill the running thread and stop the scraper.
        """
        self.RUNNING = False
        self.logger.critical(f"THREAD KILLED FOR {self}.")

    def run(self):

        self.logger.warning(f"Starting thread: {self}...")

        consecutive_failures: int = 0

        # this will include gamelog dataset
        while self.RUNNING:
            if consecutive_failures >= 10:
                self.kill()

            try:
                self.execute()
                consecutive_failures = 0
            except Exception as e:
                self.logger.warning(f"Error in {self}: {e}")
                consecutive_failures += 1
