""" Code extensible for configuration and configuration management.

Both, configuration files and (optionally) command line arguments are supported (using :mod:`configargparse`).
The configuration can be extended with custom :class:`ConfigExtension`.

The configuration can be loaded with the :class:`ConfigLoader`.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Optional

import configargparse   # type: ignore

from spotterbase.rdf.uri import Uri

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATHS: list[Path] = [p.expanduser() for p in [
    Path('~/.config/spotterbase.conf'),
    Path('~/.spotterbase.conf'),
    Path('~/spotterbase.conf'),
    Path('./.spotterbase.conf'),
    Path('./spotterbase.conf'),
]]


class ConfigExtension:
    """ Can be used to adjust anything related to ``ArgumentParser``, in particular to add further arguments. """
    def prepare_argparser(self, argparser: configargparse.ArgumentParser):
        pass

    def process_namespace(self, args: argparse.Namespace):
        pass


class ConfigLoader:
    default_extensions: list[ConfigExtension] = []

    def __init__(self, extensions: Optional[list[ConfigExtension]] = None, config_paths: Optional[list[Path]] = None):
        if extensions is None:
            extensions = self.default_extensions
        self.extensions = extensions

        if config_paths is None:
            config_paths = DEFAULT_CONFIG_PATHS

        self.used_default_config_paths: list[Path] = [path for path in config_paths if path.is_file()]
        self.argparser = configargparse.ArgumentParser(
            default_config_files=list(map(str, self.used_default_config_paths)),
            add_help=False,
            ignore_unknown_config_file_keys=True)
        self.argparser.add_argument('-c', '--config', is_config_file=True, help='config file path')
        for extension in self.extensions:
            extension.prepare_argparser(self.argparser)

    def load_from_args(self, args: Optional[list[str]] = None) -> argparse.Namespace:
        if args is None:
            args = sys.argv[1:]
        # help was previously suppressed in case it is the parent of another ``ArgumentParser``
        self.argparser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                                    help='show this help message and exit')
        namespace = self.argparser.parse_args(args=args)
        self.load_from_namespace(namespace)
        return namespace

    def load_from_namespace(self, namespace: argparse.Namespace):
        for extension in self.extensions:
            extension.process_namespace(namespace)

        used_configs = self.used_default_config_paths
        if namespace.config:
            used_configs.append(Path(namespace.config))
        if used_configs:
            logger.log(logging.INFO,
                       'The following configuration files were considered: ' + '; '.join(map(str, used_configs)))
        else:
            logger.log(logging.INFO, 'No configuration files were considered')


# LogConfigExtension should stay here to make sure that it is the first default extension
class LogConfigExtension(ConfigExtension):
    _log_level_map = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR}

    def prepare_argparser(self, argparser: configargparse.ArgumentParser):
        argparser.add_argument('--log-level', default='INFO', choices=self._log_level_map.keys(),
                               help='logging level')
        argparser.add_argument('--log-file', nargs='?', default='stdout', help='the log file (or stdout/stderr)')

    def process_namespace(self, namespace: argparse.Namespace):
        logging_config: dict[str, Any] = {
            'format': '%(process)6d %(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'level': self._log_level_map[namespace.log_level]
        }
        if namespace.log_file not in {'stdout', 'stderr'}:
            logging_config['filename'] = namespace.log_file
            logging_config['filemode'] = 'w'
        else:
            logging_config['stream'] = {'stdout': sys.stdout, 'stderr': sys.stderr}[namespace.log_file]
        logging.basicConfig(**logging_config)


ConfigLoader.default_extensions.append(LogConfigExtension())


class SimpleConfigExtension(ConfigExtension):
    value: Any

    def __init__(self, name: str, description: str, add_to_default_configs: bool = True, **kwargs):
        self.name = name
        self.description = description
        self.kwargs = kwargs
        if add_to_default_configs:
            ConfigLoader.default_extensions.append(self)
        self.__post_init__()

    def __post_init__(self):
        pass

    def prepare_argparser(self, argparser: argparse.ArgumentParser):
        argparser.add_argument(self.name, help=self.description, **self.kwargs)

    def process_namespace(self, args: argparse.Namespace):
        k = self.name.lstrip('-').replace('-', '_')
        self.value = getattr(args, k)

    def __eq__(self, other) -> bool:
        return self.value == other


class ConfigFlag(SimpleConfigExtension):
    value: bool = False

    def __post_init__(self):
        assert 'action' not in self.kwargs
        self.kwargs['action'] = 'store_true'

    def __bool__(self) -> bool:
        return self.value


class ConfigString(SimpleConfigExtension):
    value: Optional[str] = None


class ConfigInt(SimpleConfigExtension):
    value: Optional[int] = None

    def __post_init__(self):
        assert 'type' not in self.kwargs
        self.kwargs['type'] = int


class ConfigUri(SimpleConfigExtension):
    value: Optional[Uri] = None

    def __post_init__(self):
        assert 'type' not in self.kwargs
        self.kwargs['type'] = Uri


class ConfigPath(SimpleConfigExtension):
    value: Optional[Path] = None

    def __post_init__(self):
        assert 'type' not in self.kwargs
        self.kwargs['type'] = Path


def auto():
    ConfigLoader().load_from_args()