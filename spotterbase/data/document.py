import abc
from typing import IO, Iterator

from rdflib import URIRef


class Document(abc.ABC):
    def get_uri(self) -> URIRef:
        raise NotImplementedError()

    def open(self, *args, **kwargs) -> IO:
        raise NotImplementedError()


class Corpus(abc.ABC):
    def get_uri(self) -> URIRef:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Document]:
        raise NotImplementedError()
