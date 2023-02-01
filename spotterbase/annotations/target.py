from __future__ import annotations

import abc
from typing import Any

from spotterbase.annotations.conversion_base_classes import Portable
from spotterbase.annotations.selector import Selector
from spotterbase.annotations.utils import as_list
from spotterbase.rdf.base import Uri, TripleI
from spotterbase.rdf.vocab import RDF, OA
from spotterbase.sb_vocab import SB


class Target(Portable, abc.ABC):
    uri: Uri    # Must have URI to allow secondary spotters to attach another annotation

    @classmethod
    def from_json(cls, json: Any) -> Target:
        # TODO: Follow approach used by selectors instead
        match json:
            case str():
                return ExistingTarget(Uri(json))
            case {'id': uri, 'type': str(SB.document)}:
                return DocumentTarget(Uri(uri))
            case {'id': target_uri, 'source': doc_uri, 'selector': selectors}:
                return FragmentTarget(target_uri=Uri(target_uri),
                                      document_uri=Uri(doc_uri),
                                      selectors=[Selector.from_json(selector) for selector in as_list(selectors)])
            case _:
                raise Exception('Unsupported JSON content for target')


class ExistingTarget(Target):
    def __init__(self, uri: Uri):
        self.uri = uri

    def to_json(self) -> str:
        return str(self.uri)

    def to_triples(self) -> TripleI:
        """ No triples to create if target already exists """
        yield from []


class DocumentTarget(Target):
    def __init__(self, document_uri: Uri):
        self.uri = document_uri

    def to_json(self) -> dict[str, str]:
        return {'type': str(SB.document), 'id': str(self.uri)}

    def to_triples(self) -> TripleI:
        # this triple might already exist (e.g. from the corpus metadata),
        # but it seems important enough to ensure that it really exists.
        yield self.uri, RDF.type, SB.document


class FragmentTarget(Target):
    def __init__(self, target_uri: Uri, document_uri: Uri, selectors: list[Selector]):
        self.uri = target_uri
        self.document_uri = document_uri
        self.selectors = selectors

    def to_json(self) -> dict[str, Any]:
        return {
            'id': self.uri,
            'source': self.document_uri,
            'selector': [selector.to_json() for selector in self.selectors]
        }

    def to_triples(self) -> TripleI:
        yield self.uri, OA.hasSource, self.document_uri
        for selector in self.selectors:
            yield self.uri, OA.hasSelector, selector.get_rdf_node()
            yield from selector.to_triples()
