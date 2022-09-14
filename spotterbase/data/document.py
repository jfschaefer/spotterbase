import abc
from typing import IO, Iterator

from spotterbase.rdf.base import Uri


class Document(abc.ABC):
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    def open(self, *args, **kwargs) -> IO:
        raise NotImplementedError()


class DocumentNotInCorpusException(Exception):
    pass


class DocumentNotFoundException(Exception):
    pass


class Corpus(abc.ABC):
    def get_uri(self) -> Uri:
        raise NotImplementedError()

    def get_document_from_uri(self) -> Document:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Document]:
        raise NotImplementedError()
