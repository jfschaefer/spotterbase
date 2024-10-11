from pathlib import Path
from typing import IO, Iterator

from spotterbase.corpora.interface import Corpus, DocumentNotInCorpusException, Document, DocumentNotFoundError
from spotterbase.rdf.uri import Uri


class LocalDocument(Document):
    def __init__(self, uri: Uri, path: Path):
        self._uri: Uri = uri
        self._path: Path = path

    def get_uri(self) -> Uri:
        return self._uri

    def open_binary(self) -> IO[bytes]:
        return self._path.open('rb')


class _LocalCorpus(Corpus):
    def get_uri(self) -> Uri:
        return Uri('file://')

    def get_document(self, uri: Uri) -> Document:
        if not uri.starts_with('file:'):
            raise DocumentNotInCorpusException()
        if hasattr(Path, 'from_uri'):
            path = Path.from_uri(uri)
        else:
            from urllib.parse import unquote, urlparse
            path = Path(unquote(urlparse(str(uri)).path))
        if path.is_file():
            return LocalDocument(uri, path)
        raise DocumentNotFoundError(f'{path} does not exist')

    def __iter__(self) -> Iterator[Document]:
        raise Exception('Cannot iterate over local file system')


def load():
    from spotterbase.corpora.resolver import Resolver
    Resolver.register_corpus(_LocalCorpus())
