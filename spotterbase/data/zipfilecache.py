import argparse
import logging
import zipfile
from collections import deque
from pathlib import Path
from typing import List, IO, Dict, Deque, Tuple

from spotterbase.config_loader import ConfigExtension, ConfigLoader

logger = logging.getLogger(__name__)


class OpenedZipFile(zipfile.ZipFile):
    """ A zip file that is currently opened in the :class:`ZipFileCache`.

    The expiry (an integer) indicates when the zip file may be closed.
    The expiry is increased when the zip file is used. """

    def __init__(self, filename: str, expiry: int):
        zipfile.ZipFile.__init__(self, filename)
        self.expiry: int = expiry
        # we need to keep track of opened files to make sure we don't close the zip file too soon
        self.opened_files: List[IO] = []

    def open(self, *args, **kwargs) -> IO:
        """ Opens a zip file (like ``zipfile.ZipFile.open``) """
        file = super().open(*args, **kwargs)
        self.opened_files.append(file)
        return file

    def clean(self):
        """ Remove closed files from the ``opened_files`` list """
        self.opened_files = [file for file in self.opened_files if not file.closed]


class ZipFileCache(object):
    """ A cache for opened zip files """

    def __init__(self, max_open: int = 100):
        assert max_open > 0
        self.max_open = max_open

        self.zipfiles: Dict[str, OpenedZipFile] = {}   # file name -> opened zip file

        # zipfiledeque records expiry dates for opened zip files.
        # Files on the left expire earliest.
        # If the expiry is increased, a new record is appended (i.e. it may contain outdated records).
        self.zipfiledeque: Deque[Tuple[str, int]] = deque()   # pairs (file name, expiry)


        # STATISTICS
        # how often a zip file was requested
        self.stat_requested: int = 0
        # how often the zip file was already open
        self.stat_successes: int = 0
        # how often an expiry was extended because files in the zip file were closed
        self.stat_extended_because_open: int = 0

    def _make_space(self):
        """ Make sure that there is space for at least one more open zip file """
        number_of_unprocessed_records = len(self.zipfiledeque)
        while len(self.zipfiles) >= self.max_open and number_of_unprocessed_records:
            number_of_unprocessed_records -= 1
            name, expiry = self.zipfiledeque.popleft()
            ozf = self.zipfiles[name]
            ozf.clean()
            if ozf.expiry == expiry:    # otherwise it's an outdated record
                if not ozf.opened_files:
                    self.zipfiles[name].close()
                    del self.zipfiles[name]
                else:
                    self.stat_extended_because_open += 1
                    self._push_back(ozf, name)
        if len(self.zipfiles) >= self.max_open:
            raise Exception('Failed to make space for another zip file - make sure that all files were closed.')

    def _push_back(self, ozf: OpenedZipFile, name: str):
        """ adds a new record for ozf and increases the expiry """
        ozf.expiry = self.zipfiledeque[-1][1] + 1
        self.zipfiledeque.append((name, ozf.expiry))

    def _remove_outdated_records(self):
        old = self.zipfiledeque
        self.zipfiledeque = deque()
        for e in old:
            if self.zipfiles[e[0]].expiry == e[1]:
                self.zipfiledeque.append(e)

    def __getitem__(self, path: Path) -> zipfile.ZipFile:
        self.stat_requested += 1
        name = str(path.resolve())
        if name not in self.zipfiles:
            expiry = self.zipfiledeque[-1][1] + 1 if len(self.zipfiledeque) else 0
            ozf = OpenedZipFile(name, expiry=expiry)
            self.zipfiles[name] = ozf
            self.zipfiledeque.append((name, expiry))
            self._make_space()
            return ozf
        else:
            self.stat_successes += 1
            ozf = self.zipfiles[name]
            self._push_back(ozf, name)
            if len(self.zipfiledeque) > 20 * self.max_open:
                self._remove_outdated_records()
            return ozf

    def close(self):
        """ Close the zip file cache """
        for zf in self.zipfiles.values():
            zf.clean()
            if zf.opened_files:
                logger.warning(f'{zf.filename} still has open files')
            zf.close()

    def __del__(self):
        self.close()


class SharedZipFileCacheExtension(ConfigExtension):
    def prepare_argparser(self, argparser: argparse.ArgumentParser):
        argparser.add_argument('--max-open-zipfiles', help='maximum number of zip files opened in parallel',
                               default=500, type=int)

    def process_namespace(self, args: argparse.Namespace):
        SHARED_ZIP_CACHE.max_open = args.max_open_zipfiles


SHARED_ZIP_CACHE = ZipFileCache()
ConfigLoader.default_extensions.append(SharedZipFileCacheExtension())
