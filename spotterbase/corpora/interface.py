import abc
from typing import IO, Iterator

from spotterbase.rdf.base import Uri


class Document(abc.ABC):
    @abc.abstractmethod
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    @abc.abstractmethod
    def open(self, *args, **kwargs) -> IO:
        raise NotImplementedError()


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
