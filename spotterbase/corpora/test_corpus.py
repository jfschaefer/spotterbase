from pathlib import Path
from typing import IO, Iterator

from spotterbase.corpora.interface import Corpus, DocumentNotInCorpusException, Document, DocumentNotFoundError
from spotterbase.rdf.uri import Uri
from spotterbase.model_core.sb import SB

TEST_CORPUS_URI: Uri = SB.NS['test-corpus/']


class TestDocument(Document):
    def __init__(self, uri: Uri, path: Path):
        self._uri: Uri = uri
        self._path: Path = path

    def get_uri(self) -> Uri:
        return self._uri

    def open_binary(self) -> IO[bytes]:
        return self._path.open('rb')


class _TestCorpus(Corpus):
    def get_uri(self) -> Uri:
        return TEST_CORPUS_URI

    def get_document(self, uri: Uri) -> Document:
        if not uri.starts_with(TEST_CORPUS_URI):
            raise DocumentNotInCorpusException()
        doc_name = uri.relative_to(TEST_CORPUS_URI)
        path = Path(__file__).parent / 'test_corpus_data' / f'{doc_name}.html'
        if path.is_file():
            return TestDocument(uri, path)
        raise DocumentNotFoundError(f'{path} does not exist')

    def __iter__(self) -> Iterator[Document]:
        directory = Path(__file__).parent / 'test_corpus_data'
        for path in sorted(directory.glob('*.html')):
            uri = TEST_CORPUS_URI / path.name.removesuffix('.html')
            yield TestDocument(uri, path)


TEST_CORPUS: Corpus = _TestCorpus()

TEST_DOC_A: Document = TEST_CORPUS.get_document(TEST_CORPUS_URI / 'paperA')


def load():
    from spotterbase.corpora.resolver import Resolver
    Resolver.register_corpus(TEST_CORPUS)
