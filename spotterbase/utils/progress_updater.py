import abc
import dataclasses
import datetime
import time
from typing import Optional


class PrintTimerStrategy(abc.ABC):
    @abc.abstractmethod
    def get_delay_in_sec(self) -> float:
        ...


@dataclasses.dataclass
class FixedDelay(PrintTimerStrategy):
    delay_in_secs: float = 5

    def get_delay_in_sec(self) -> float:
        return self.delay_in_secs


class IncreasingDelay(PrintTimerStrategy):
    """ Increases the delay to show frequent updates initially without j"""
    def __init__(self, start_delay_secs: float, end_delay_secs: float):
        self.start_delay_secs: float = start_delay_secs
        self.end_delay_secs: float = end_delay_secs
        self.start_time: float = time.time()

    def get_delay_in_sec(self) -> float:
        inc_time = self.end_delay_secs * 3
        return self.start_delay_secs + \
            (time.time() - self.start_time) / inc_time * (self.end_delay_secs - self.start_delay_secs)


class ProgressUpdater:
    """ Prints regular messages about the progress of a large task.

     Note that it does not start a background thread and only considers
     creating a log when :meth:`update` is called.
     """
    def __init__(self, message: str, timer_strategy: Optional[PrintTimerStrategy] = None):
        """ ``message`` should be a string that has a placeholder ``"progress"``.
            For example, ``message`` could be
            :code:`"Progress update: {progress} documents were processed"`.
        """
        self.message = message
        self.timer_strategy = timer_strategy or FixedDelay(delay_in_secs=5)
        self.last_message = time.time()

    def update(self, progress):
        """ Logs the ``progress`` iff enough time has passed since the last log message."""
        now = time.time()
        if now - self.last_message > self.timer_strategy.get_delay_in_sec():
            self.last_message = now
            print(datetime.datetime.now().isoformat(), self.message.format(progress=progress))
