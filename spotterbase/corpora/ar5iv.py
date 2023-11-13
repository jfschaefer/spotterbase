import logging
from io import StringIO
from typing import IO, Iterator

import requests

from spotterbase.corpora.arxiv import ArxivId
from spotterbase.corpora.interface import Document, DocumentNotFoundError, Corpus, DocumentNotInCorpusException
from spotterbase.rdf import Uri
from spotterbase.utils.logging import warn_once

logger = logging.getLogger(__name__)


class Ar5ivDoc(Document):
    def __init__(self, identifier: ArxivId):
        self.identifier = identifier

    def get_uri(self) -> Uri:
        return Uri('https://ar5iv.org/abs') / str(self.identifier)

    def open(self, *args, **kwargs) -> IO:
        # TODO: Caching
        try:
            result = requests.get(str(self.get_uri()))
        except requests.exceptions.ConnectionError:
            raise DocumentNotFoundError(f'Failed to load {self.get_uri()} (connection error)')
        if result.status_code != 200:
            raise DocumentNotFoundError(f'Failed to load {self.get_uri()} (response code {result.status_code})')
        warn_once(logger, 'ar5iv.org documents may change over time. '
                          'As SpotterBase assumes a frozen corpus, this may lead to unexpected problems.')
        return StringIO(requests.get(str(self.get_uri())).text)


class Ar5ivCorpus(Corpus):
    def get_uri(self) -> Uri:
        return Uri('https://ar5iv.org/')

    def get_document(self, uri: Uri) -> Document:
        prefix = 'https://ar5iv.org/abs/'
        if not uri.starts_with(prefix):
            raise DocumentNotInCorpusException()
        return Ar5ivDoc(ArxivId(str(uri)[len(prefix):]))

    def __iter__(self) -> Iterator[Document]:
        raise NotImplementedError('The ar5iv corpus is not iterable.')


AR5IV_CORPUS: Ar5ivCorpus = Ar5ivCorpus()
