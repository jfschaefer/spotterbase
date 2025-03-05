import atexit
import datetime
import logging
from collections import OrderedDict
from io import BytesIO
import shelve
from typing import IO, Iterator, Optional

import requests

from spotterbase.plugins.arxiv.arxiv import ArxivId
from spotterbase.corpora.interface import Document, DocumentNotFoundError, Corpus, DocumentNotInCorpusException
from spotterbase.data.locator import CacheDir
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

        TODO: The current implementation is not thread-safe...
    """
    shelve: shelve.Shelf
    usages: OrderedDict[str, datetime.datetime]

    def __init__(self):
        pass

    def require_shelve(self):
        if not hasattr(self, 'shelve'):
            logger.info('Opening ar5iv cache at ' + str(CacheDir.get() / 'ar5iv_cache'))
            self.shelve = shelve.open(CacheDir.get() / 'ar5iv_cache', writeback=True)
            self.usages = self.shelve.setdefault('usages', OrderedDict())
            self.shelve.sync()
            assert len(self.usages) == len(self.shelve) - 1
            atexit.register(self.shelve.close)

    def get(self, identifier: Uri) -> Optional[bytes]:
        strid = str(identifier)
        self.require_shelve()
        if strid in self.usages:
            if self.usages[strid] < datetime.datetime.now() - datetime.timedelta(days=1):
                del self.shelve[strid]
                del self.usages[strid]
                self.shelve['usages'] = self.usages
                self.shelve.sync()
                return None
            self.usages.move_to_end(strid)
            self.shelve['usages'] = self.usages
            self.shelve.sync()
            r = self.shelve[strid]
            assert r is not None
        return None

    def put(self, identifier: Uri, content: bytes):
        self.require_shelve()
        self.usages[str(identifier)] = datetime.datetime.now()
        self.shelve[str(identifier)] = content
        if len(self.usages) > 20:
            # potential optimization: first remove all expired entries (could also be done during initializations)
            least_recently_used = self.usages.popitem(last=False)[0]
            del self.shelve[least_recently_used]
        self.shelve['usages'] = self.usages
        self.shelve.sync()


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
