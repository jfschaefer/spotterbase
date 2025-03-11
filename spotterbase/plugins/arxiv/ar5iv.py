import atexit
import datetime
import logging
import zlib
from io import BytesIO
from typing import IO, Iterator, Optional

import diskcache
import requests

from spotterbase.corpora.interface import Document, DocumentNotFoundError, Corpus, DocumentNotInCorpusException
from spotterbase.data.locator import CacheDir
from spotterbase.plugins.arxiv.arxiv import ArxivId
from spotterbase.rdf import Uri
from spotterbase.utils.logging import warn_once

logger = logging.getLogger(__name__)


class _Ar5ivCache:
    """
        Ar5iv documents are downloaded from ar5iv.org on demand.
        ar5iv.org is not fixed. E.g. documents may be re-created with newer LaTeXML versions.
        That makes ar5iv documents unsuitable for larger annotation projects
        (of course a frozen version of ar5iv would be very suitable).
        Regardless, ar5iv documents are used often in practice for examples as they are easy to access.
        This usage means that a few example documents are frequently downloaded.

        This class acts as a cache that stores a small number of most recently used documents
        and discards them after a while.
    """
    cache: diskcache.Cache

    def __init__(self):
        pass

    def _require_cache(self):
        if not hasattr(self, 'cache'):
            logger.info('Opening ar5iv cache at ' + str(CacheDir.get() / 'ar5iv_cache'))
            self.cache = diskcache.Cache(
                str(CacheDir.get() / 'ar5iv_cache'),
                size_limit=2 ** 25,  # 32 MiB
            )
            atexit.register(self.cache.close)

    def get(self, identifier: Uri) -> Optional[bytes]:
        self._require_cache()
        if str(identifier) in self.cache:
            return zlib.decompress(self.cache[str(identifier)])
        return None

    def put(self, identifier: Uri, content: bytes):
        self._require_cache()
        self.cache.set(
            str(identifier),
            zlib.compress(content, level=1),
            expire=datetime.timedelta(days=1).total_seconds()
        )


_AR5IV_CACHE = _Ar5ivCache()


class Ar5ivDoc(Document):
    def __init__(self, identifier: ArxivId):
        self.identifier = identifier

    def get_uri(self) -> Uri:
        return Uri('https://ar5iv.org/abs') / str(self.identifier)

    def open_binary(self) -> IO[bytes]:
        warn_once(logger, 'ar5iv.org documents may change over time. '
                          'As SpotterBase assumes a frozen corpus, this may lead to unexpected problems.')
        cached_result = _AR5IV_CACHE.get(self.get_uri())
        if cached_result is not None:
            return BytesIO(cached_result)
        try:
            result = requests.get(str(self.get_uri()))
        except requests.exceptions.ConnectionError:
            raise DocumentNotFoundError(f'Failed to load {self.get_uri()} (connection error)')
        if result.status_code != 200:
            raise DocumentNotFoundError(f'Failed to load {self.get_uri()} (response code {result.status_code})')
        content = requests.get(str(self.get_uri())).content
        _AR5IV_CACHE.put(self.get_uri(), content)
        return BytesIO(content)


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
