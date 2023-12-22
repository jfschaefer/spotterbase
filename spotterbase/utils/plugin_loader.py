"""Loads SpotterBase plugins.

load_plugins is called from spotterbase.__init__
"""
import dataclasses
import functools
import logging
import traceback
import warnings
from importlib.metadata import entry_points
from typing import Optional

plugins_loaded: bool = False


@dataclasses.dataclass
class LoadingStatus:
    error: Optional[str] = None
    message: Optional[str] = None


loading_results: dict[str, LoadingStatus] = {}


@functools.cache   # load them only once
def load_core_plugins():
    import spotterbase.model_core
    import spotterbase.corpora.test_corpus

    spotterbase.model_core.load()
    spotterbase.corpora.test_corpus.load()


def load_plugins():
    global plugins_loaded
    if plugins_loaded:
        warnings.warn('Plugins have already been loaded')
        return
    plugins_loaded = True

    load_core_plugins()

    discovered_plugins = entry_points(group='spotterbase.plugins')
    for plugin in discovered_plugins:
        try:
            module = plugin.load()
            message = None
            if hasattr(module, 'load'):
                message = module.load()
            if message:
                assert isinstance(message, str)
            loading_results[plugin.name] = LoadingStatus(message=message or 'Successfully loaded')
        except Exception as e:
            stacktrace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            loading_results[plugin.name] = LoadingStatus(error=stacktrace)


def log_plugin_loading_results():
    """Logging is only configured after plugins are loaded."""
    logger = logging.getLogger(__name__)
    logger.info(f'Loaded {len(loading_results)} plugins during start-up, here are the results:')
    for plugin_name, status in loading_results.items():
        if status.error:
            logger.error(f'Failed to load plugin {plugin_name}:')
            logger.error(status.error)
        else:
            logger.info(f'Successfully loaded plugin {plugin_name}: {status.message}')
