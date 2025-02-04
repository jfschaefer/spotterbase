import logging
import tempfile
from pathlib import Path
from typing import Optional, Iterator

from spotterbase.utils.config_loader import SimpleConfigExtension, _Group

logger = logging.getLogger(__name__)


class LocatorFailedException(Exception):
    pass


class Locator(SimpleConfigExtension):
    def __init__(self, name: str, description: str, default_rel_locations: list[Path | str],
                 how_to_get: Optional[str] = None, group: Optional[_Group] = None):
        super().__init__(
            name=name,
            description=description,
            group=group
        )
        self.how_to_get = how_to_get
        self.default_rel_locations = default_rel_locations

    def is_located(self) -> bool:
        return self.location_opt() is not None

    def default_locations(self) -> Iterator[Path]:
        for rel in self.default_rel_locations:
            yield DataDir.get(rel)

    def location_opt(self) -> Optional[Path]:
        if not hasattr(self, 'value'):
            raise RuntimeError('The locator appears uninitialized. Did you run spotterbase.utils.config_loader.auto()?')
        if self.value:
            return Path(self.value)
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
            message += \
                f'. If you have the dataset in a different location, you can specify it using {self.name}=<path>'
            raise LocatorFailedException(message)
        return path


class DataDir:
    data_locator = Locator('--data-path', 'the data directory', [])

    @classmethod
    def get(cls, rel_path: Path | str) -> Path:
        path = cls.data_locator.location_opt() or Path('~/spotterbase-data').expanduser()
        if not path.exists():
            path.mkdir()
        return path / rel_path


class CacheDir:
    cache_locator = Locator('--cache-dir', 'directory for caching data', [])

    @classmethod
    def get(cls, rel_path: Optional[Path | str] = None) -> Path:
        path = cls.cache_locator.location_opt() or DataDir.get('cache')
        if not path.exists():
            path.mkdir()
        if rel_path:
            path = path / rel_path
        return path


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
