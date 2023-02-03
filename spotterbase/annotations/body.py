from __future__ import annotations

import abc
from typing import Optional, Any

from spotterbase.annotations.serialization_abc import Portable
from spotterbase.annotations.utils import RdfNodeMixin
from spotterbase.rdf.base import Uri, TripleI
from spotterbase.rdf.vocab import RDF
from spotterbase.sb_vocab import SB


class Body(Portable, RdfNodeMixin, abc.ABC):
    @classmethod
    def from_json(cls, json: Any) -> Body:
        match json['type']:
            case 'SimpleTagBody':
                return SimpleTagBody.from_json(json)
            case other:
                raise Exception(f'Unsupported body type: {other}')


class SimpleTagBody(Body):
    def __init__(self, tag: Uri, body_uri: Optional[Uri]):
        self.tag: Uri = tag
        if body_uri:
            self.set_rdf_node(body_uri)

    @classmethod
    def from_json(cls, json: Any) -> SimpleTagBody:
        assert json['type'] == 'SimpleTagBody'
        return SimpleTagBody(Uri(json['val']), body_uri=Uri(json['id']) if 'id' in json else None)

    def to_json(self) -> dict[str, str]:
        d = {'type': 'SimpleTagBody', 'val': str(self.tag)}
        if self.has_rdf_uri():
            d['id'] = str(self.get_rdf_node())
        return d

    def to_triples(self) -> TripleI:
        yield self.get_rdf_node(), RDF.type, SB.SimpleTagBody
        yield self.get_rdf_node(), RDF.value, self.tag
