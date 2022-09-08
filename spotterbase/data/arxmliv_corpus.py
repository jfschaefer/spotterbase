import abc
import argparse
import re
from pathlib import Path
from typing import IO, Iterator, Optional

from rdflib import URIRef

from spotterbase.config_loader import ConfigExtension, ConfigLoader
from spotterbase.data.arxiv_metadata import ArxivId
from spotterbase.data.locator import Locator
from spotterbase.data.utils import MissingDataException
from spotterbase.data.zipfilecache import SHARED_ZIP_CACHE


class ArXMLivUris:
    arxmliv = URIRef(f'http://sigmathling.kwarc.info/arxmliv/')

    severity = URIRef(arxmliv + 'severity/')
    severity_no_problem = URIRef(severity + 'noProblem')
    severity_warning = URIRef(severity + 'warning')
    severity_error = URIRef(severity + 'error')


class ArXMLivDocument(abc.ABC):
    arxivid: ArxivId
    release: str

    def __init__(self, arxivid: ArxivId, release: str):
        self.arxivid = arxivid
        self.release = release

    def get_uri(self) -> URIRef:
        return ArXMLiv.get_release_uri(self.release) + self.arxivid.identifier

    def open(self, *args, **kwargs) -> IO:
        raise NotImplementedError()


class SimpleArXMLivDocument(ArXMLivDocument):
    def __init__(self, arxivid: ArxivId, release: str, path: Path):
        super().__init__(arxivid, release)
        self.path = path

    def open(self, *args, **kwargs) -> IO:
        return self.path.open(*args, **kwargs)


class ZipArXMLivDocument(ArXMLivDocument):
    def __init__(self, arxivid: ArxivId, release: str, path_to_zipfile: Path, filename: str):
        super().__init__(arxivid, release)
        self.path_to_zipfile = path_to_zipfile
        self.filename = filename

    def open(self, *args, **kwargs) -> IO:
        zf = SHARED_ZIP_CACHE[self.path_to_zipfile]
        try:
            return zf.open(self.filename, *args, **kwargs)
        except KeyError as e:
            missing = MissingDataException(f'Failed to find {self.filename} in {self.path_to_zipfile}: {e}')
            missing.__suppress_context__ = True
            raise missing


class ArXMLivCorpus:
    filename_regex = re.compile(f'^(?P<oldprefix>[a-z-]+)?(?P<digits>[0-9.]+).html$')

    def __init__(self, release: str, path: Path):
        self.release = release
        self.path = path

    def get_document(self, arxivid: ArxivId) -> ArXMLivDocument:
        location = self._get_yymm_location(arxivid.yymm)
        if location.name.endswith('.zip'):
            return ZipArXMLivDocument(arxivid, self.release, location,
                               f'{arxivid.yymm}/{arxivid.identifier.replace("/", "")}.html')
        else:
            return SimpleArXMLivDocument(arxivid, self.release, location)

    def _get_yymm_location(self, yymm: str) -> Path:
        for directory in [self.path / f'{yymm}', self.path / 'data' / f'{yymm}']:
            if directory.is_dir():
                return directory
        for zip_path in [self.path / f'{yymm}.zip', self.path / 'data' / f'{yymm}.zip']:
            if zip_path.is_file():
                return zip_path
        raise MissingDataException(f'Failed to find a folder for "{yymm}" in {self.path}')

    def _iter_yymm_locations(self) -> Iterator[Path]:
        if not (path := self.path / 'data').is_dir():
            path = self.path
        path_regex = re.compile(r'^[0-9][0-9][0-9][0-9](\.zip)?$')
        for content in path.iterdir():
            if path_regex.match(content.name):
                yield content

    @classmethod
    def filename_to_arxivid_or_none(cls, filename: str) -> Optional[ArxivId]:
        if match := cls.filename_regex.match(filename):
            if match.group('oldprefix'):
                return ArxivId(match.group('oldprefix') + '/' + match.group('digits'))
            else:
                return ArxivId(match.group('digits'))
        return None

    def __iter__(self) -> Iterator[ArXMLivDocument]:
        for yymm_location in self._iter_yymm_locations():
            if yymm_location.is_dir():
                for path in yymm_location.iterdir():
                    if arxivid := self.filename_to_arxivid_or_none(path.name):
                        yield SimpleArXMLivDocument(arxivid, self.release, path)
            else:
                assert yymm_location.name.endswith('.zip')
                for name in SHARED_ZIP_CACHE[yymm_location].namelist():
                    if arxivid := self.filename_to_arxivid_or_none(name.split('/')[-1]):
                        yield ZipArXMLivDocument(arxivid, self.release, yymm_location, name)


class ArXMLivConfig(ConfigExtension):
    # All supported arXMLiv releases (ordered by release date)
    releases: list[str] = ['08.2017', '08.2018', '08.2019', '2020']

    def __init__(self):
        self.locators: dict[str, Locator] = {}
        for release in self.releases:
            self.locators[release] = Locator(f'--arxmliv-{release}-path',
                                             description=f'path to the {release} arXMLiv release',
                                             default_rel_locations=[f'arxmliv-{release}', f'arxmliv-{release}.tar.gz'],
                                             how_to_get=f'SIGMathLing members can download the arXMLiv copora from https://sigmathling.kwarc.info/resources/')

#     def prepare_argparser(self, argparser: argparse.ArgumentParser):
#         argparser.add_argument('--default-arxmliv-release', help='default release of the arXMLiv corpus',
#                                choices=self.releases, default=self.releases[-1])


class ArXMLiv:
    config = ArXMLivConfig()
    ConfigLoader.default_extensions.append(config)

    def get_corpus(self, release: str) -> ArXMLivCorpus:
        assert release in ArXMLivConfig.releases, f'Unknown arXMLiv release "{release}"'
        return ArXMLivCorpus(release, self.config.locators[release].require())

    @classmethod
    def get_release_uri(cls, release: str) -> URIRef:
        return URIRef(ArXMLivUris.arxmliv + release + '/')

