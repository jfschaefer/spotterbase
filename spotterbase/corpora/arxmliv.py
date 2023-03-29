import abc
import re
from pathlib import Path
from typing import IO, Iterator, Optional

from spotterbase.corpora.arxiv import ArxivId
from spotterbase.corpora.interface import Document, Corpus, DocumentNotFoundError, CannotLocateCorpusDataError, \
    DocumentNotInCorpusException
from spotterbase.data.locator import Locator, LocatorFailedException
from spotterbase.data.zipfilecache import SHARED_ZIP_CACHE
from spotterbase.rdf.uri import Uri
from spotterbase.anno_core.sb import SB

ARXMLIV_RELEASES: list[str] = ['08.2017', '08.2018', '08.2019', '2020']


class ArXMLivUris:
    arxmliv = Uri('http://sigmathling.kwarc.info/arxmliv/')

    severity = arxmliv / 'severity/'
    severity_no_problem = severity / 'noProblem'
    severity_warning = severity / 'warning'
    severity_error = severity / 'error'

    @classmethod
    def get_corpus_uri(cls, release: str, centi: bool = False) -> Uri:
        if centi:
            return ArXMLivUris.arxmliv / 'centi' / release + '/'
        return ArXMLivUris.arxmliv / release + '/'

    @classmethod
    def get_metadata_graph_uri(cls, release: str) -> Uri:
        return SB.NS['graph/arxmliv-meta/' + release]


class ArXMLivDocument(Document, abc.ABC):
    arxivid: ArxivId
    release: str

    def __init__(self, arxivid: ArxivId, release: str):
        self.arxivid = arxivid
        self.release = release

    def get_uri(self) -> Uri:
        return ArXMLivUris.get_corpus_uri(self.release) + self.arxivid.identifier

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
            # Creating zipfile.Path overwrites __class__, which is a problem as we are subclassing...
            # return (zipfile.Path(zf) / self.filename).open(*args, **kwargs)
            return zf.open(self.filename, *args, **kwargs)
        except KeyError as e:
            missing = DocumentNotFoundError(f'Failed to find {self.filename} in {self.path_to_zipfile}: {e}')
            missing.__suppress_context__ = True
            raise missing


class ArXMLivCorpus(Corpus):
    filename_regex = re.compile(r'^(?P<oldprefix>[a-z-]+)?(?P<digits>[0-9.]+).html$')

    def __init__(self, release: str, centi: bool = False):
        self.release = release
        self._locator: Locator = Locator(
            f'--arxmliv-{release}-{"centi-" if centi else ""}path',
            description=f'path to the {release} arXMLiv release',
            default_rel_locations=[f'arxmliv-{release}'],
            how_to_get='SIGMathLing members can download the arXMLiv copora from ' +
                       'https://sigmathling.kwarc.info/resources/')
        self._centi = centi
        self._uri: Uri = ArXMLivUris.get_corpus_uri(release, centi)

    def get_document_by_id(self, arxivid: ArxivId) -> ArXMLivDocument:
        if self._centi and not arxivid.is_in_centi_arxiv():
            raise DocumentNotInCorpusException(
                'The document may be in the arXMLiv corpus, but it is not in the centi arXMLiv corpus'
            )
        location = self._get_yymm_location(arxivid.yymm)
        if location.name.endswith('.zip'):
            return ZipArXMLivDocument(arxivid, self.release, location,
                                      f'{arxivid.yymm}/{arxivid.identifier.replace("/", "")}.html')
        else:
            return SimpleArXMLivDocument(arxivid, self.release, location)

    def get_uri(self) -> Uri:
        return self._uri

    def get_document(self, uri: Uri) -> Document:
        if not uri.starts_with(self._uri):
            raise DocumentNotInCorpusException()
        return self.get_document_by_id(ArxivId(uri.relative_to(self._uri)))

    def get_path(self) -> Path:
        try:
            return self._locator.require()
        except LocatorFailedException as e:
            raise CannotLocateCorpusDataError(e)

    def _get_yymm_location(self, yymm: str) -> Path:
        path = self.get_path()
        for directory in [path / f'{yymm}', path / 'data' / f'{yymm}']:
            if directory.is_dir():
                return directory
        for zip_path in [path / f'{yymm}.zip', path / 'data' / f'{yymm}.zip']:
            if zip_path.is_file():
                return zip_path
        raise DocumentNotFoundError(f'Failed to find a folder for "{yymm}" in {path}')

    def _iter_yymm_locations(self) -> Iterator[Path]:
        if not (path := self.get_path() / 'corpora').is_dir():
            path = self.get_path()
        path_regex = re.compile(r'^[0-9][0-9][0-9][0-9](\.zip)?$')
        if (path / 'data').is_dir():
            path = path / 'data'
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
                        if self._centi and not arxivid.is_in_centi_arxiv():
                            continue
                        yield SimpleArXMLivDocument(arxivid, self.release, path)
            else:
                assert yymm_location.name.endswith('.zip')
                for name in SHARED_ZIP_CACHE[yymm_location].namelist():
                    if arxivid := self.filename_to_arxivid_or_none(name.split('/')[-1]):
                        if self._centi and not arxivid.is_in_centi_arxiv():
                            continue
                        yield ZipArXMLivDocument(arxivid, self.release, yymm_location, name)


ARXMLIV_CORPORA: dict[str, ArXMLivCorpus] = {
    release: ArXMLivCorpus(release=release) for release in ARXMLIV_RELEASES
}

CENTI_ARXMLIV_CORPORA: dict[str, ArXMLivCorpus] = {
    release: ArXMLivCorpus(release=release, centi=True) for release in ARXMLIV_RELEASES
}
