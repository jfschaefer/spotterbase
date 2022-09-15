import argparse
import logging
import tempfile
from pathlib import Path
from typing import Optional, Iterator

from spotterbase.config_loader import ConfigExtension, ConfigLoader

logger = logging.getLogger(__name__)


class LocatorFailedException(Exception):
    pass


class Locator(ConfigExtension):
    def __init__(self, arg_name: str, description: str, default_rel_locations: list[Path | str],
                 how_to_get: Optional[str] = None, add_to_default_configs: bool = True):
        self.arg_name = arg_name
        self.description = description
        self.how_to_get = how_to_get
        self.default_rel_locations = default_rel_locations

        self.specified_location: Optional[str] = None

        if add_to_default_configs:
            ConfigLoader.default_extensions.append(self)

    def prepare_argparser(self, argparser: argparse.ArgumentParser):
        argparser.add_argument(self.arg_name, help=self.description)

    def process_namespace(self, args: argparse.Namespace):
        k = self.arg_name.lstrip('-').replace('-', '_')
        if k in args:
            value = getattr(args, k)
            if value:
                self.specified_location = value

    def is_located(self) -> bool:
        return self.location_opt() is not None

    def default_locations(self) -> Iterator[Path]:
        for rel in self.default_rel_locations:
            yield DataDir.get(rel)

    def location_opt(self) -> Optional[Path]:
        if self.specified_location:
            return Path(self.specified_location)
        for path in self.default_locations():
            if path.exists():
                return path
        return None

    def require(self) -> Path:
        path = self.location_opt()
        if path is None:
            message = f'Failed to locate {self.description} after trying the following default locations: ' + \
                      ', '.join(map(str, self.default_locations()))
            if self.how_to_get:
                message += f'. {self.how_to_get}'
            raise LocatorFailedException(message)
        return path


class DataDir:
    data_locator = Locator('--data-path', 'the data directory', [])

    @classmethod
    def get(cls, rel_path: Path | str) -> Path:
        path = cls.data_locator.location_opt() or Path('~/spotterbase-data')
        if not path.exists():
            path.mkdir()
        return path / rel_path


class TmpDir:
    locator = Locator('--tmp-dir', 'directory for temporary data', [])

    _tmp_path: Optional[Path] = None

    @classmethod
    def get(cls, rel_path: Optional[Path | str] = None) -> Path:
        if not cls._tmp_path:
            cls._tmp_path = cls.locator.location_opt()
            if not cls._tmp_path:
                cls._tmp_path = Path(tempfile.gettempdir()) / 'spotterbase'
                logger.info(f'Using {cls._tmp_path} for temporary files')

            if not cls._tmp_path.exists():
                cls._tmp_path.mkdir()
        if rel_path:
            return cls._tmp_path / rel_path
        return cls._tmp_path
