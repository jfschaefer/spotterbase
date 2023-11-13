import functools
import logging


@functools.cache
def warn_once(logger: logging.Logger, message: str):
    logger.warning(message)
