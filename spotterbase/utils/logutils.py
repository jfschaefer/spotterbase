import logging
import time


class ProgressLogger:
    """ Creates regular log messages about the progress of a large task.

     Note that it does not start a background thread and only considers
     creating a log message when :meth:`update` is called.
     """
    def __init__(self, logger: logging.Logger, message: str, interval_in_secs: int = 5):
        """ ``message`` should be a string that has a placeholder ``"progress"``.
            For example, ``message`` could be
            :code:`"Progress update: {progress} documents were processed"`.
        """
        self.logger = logger
        self.message = message
        self.interval_in_secs = interval_in_secs
        self.last_message = time.time()

    def update(self, progress):
        """ Logs the ``progress`` iff enough time has passed since the last log message."""
        now = time.time()
        if now - self.last_message > self.interval_in_secs:
            self.last_message = now
            self.logger.info(self.message.format(progress=progress))
