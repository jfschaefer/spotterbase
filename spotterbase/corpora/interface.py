import abc
from typing import IO, Iterator, Optional

from lxml.etree import _ElementTree
import lxml.etree as etree

from spotterbase.rdf.uri import Uri


class Document(abc.ABC):
    _html_tree: Optional[_ElementTree] = None

    @abc.abstractmethod
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    @abc.abstractmethod
    def open(self, *args, **kwargs) -> IO:
        raise NotImplementedError()

    def get_html_tree(self, cached: bool) -> _ElementTree:
        if cached and self._html_tree is not None:
            return self._html_tree
        with self.open() as fp:
            tree: _ElementTree = etree.parse(fp, parser=etree.HTMLParser())  # type: ignore
        if cached:
            self._html_tree = tree
        return tree


class DocumentNotInCorpusException(Exception):
    """ The requested document is not part of the corpus """
    pass


class DocumentNotFoundError(Exception):
    """ If the document exists, it is part of the corpus,
    but it cannot be found right now (e.g. the file does not exist). """
    pass


class CannotLocateCorpusDataError(Exception):
    """ The corpus data cannot be found (e.g. because no path was provided) """
    pass


class Corpus(abc.ABC):
    @abc.abstractmethod
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_document(self, uri: Uri) -> Document:
        """ Should throw DocumentNotInCorpusException if necessary! """
        raise NotImplementedError()

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Document]:
        raise NotImplementedError()

    def get_documents(self) -> Iterator[Document]:
        return iter(self)
