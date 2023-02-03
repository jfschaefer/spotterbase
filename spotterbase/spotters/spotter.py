from __future__ import annotations

import abc
from typing import Iterator, Callable

from spotterbase.annotations.annotation import Annotation
from spotterbase.corpora.interface import Document
from spotterbase.rdf.base import Uri


class Spotter(abc.ABC):
    # You can set these
    spotter_short_id: str     # short id of spotter (e.g. to make unique URIs for annotations)

    # These are set by the constructor
    run_uri: Uri

    def __init__(self, run_uri: Uri):
        self.run_uri = run_uri

    @abc.abstractmethod
    def process_document(self, document: Document) -> Iterator[Annotation]:
        ...


class UriGeneratorMixin(Spotter, abc.ABC):
    def get_uri_generator_for(self, document: Document) -> UriGenerator:
        return UriGenerator(document.get_uri() + f'#{self.spotter_short_id}')


class UriGenerator:
    def __init__(self, base_uri: Uri):
        self.base_uri: Uri = base_uri
        self.counter: int = 0

    def __next__(self) -> Callable[[str], Uri]:
        count = self.counter
        self.counter += 1
        return lambda type_: self.base_uri + f'.{type_}.{count}'
