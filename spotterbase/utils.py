import logging
import time

from spotterbase.__version__ import VERSION


def version_string() -> str:
    return '.'.join(str(e) for e in VERSION)


class ProgressLogger:
    """ Creates regular log messages about the progress of a large task """
    def __init__(self, logger: logging.Logger, message: str, interval_in_secs: int = 5):
        self.logger = logger
        self.message = message
        self.interval_in_secs = interval_in_secs
        self.last_message = time.time()

    def update(self, progress):
        now = time.time()
        if now - self.last_message > self.interval_in_secs:
            self.last_message = now
            self.logger.info(self.message.format(progress=progress))
