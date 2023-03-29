from __future__ import annotations

import abc
from typing import Callable, Optional

from spotterbase.corpora.interface import Document
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.uri import Uri


class SpotterContext:
    run_uri: Uri

    def __init__(self, run_uri: Optional[Uri] = None):
        self.run_uri = Uri.uuid() if run_uri is None else run_uri


class Spotter(abc.ABC):
    # You can set these
    spotter_short_id: str     # short id of spotter (e.g. to make unique URIs for anno_core)

    # These are set by the constructor
    ctx: SpotterContext

    def __init__(self, ctx: SpotterContext):
        self.ctx = ctx

    @classmethod
    def setup_run(cls, **kwargs) -> tuple[SpotterContext, TripleI]:
        return SpotterContext(run_uri=Uri.uuid()), iter(())

    @abc.abstractmethod
    def process_document(self, document: Document) -> TripleI:
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
