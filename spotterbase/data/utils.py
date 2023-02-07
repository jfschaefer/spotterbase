import functools
import logging

logger = logging.getLogger(__name__)


@functools.cache  # cache it to avoid repeated warnings
def json_lib():
    """ Attempts to load a faster JSON library than provided by the standard library.

        Note:
            This code is intentionally a separate function to make sure that the logging configuration has been loaded.
    """
    try:
        import orjson as json     # type: ignore
    except ModuleNotFoundError:
        logger.warning(f'Could not find optional dependency `orjson` – falling back to the standard library (slower)')
        import json     # type: ignore
    return json
