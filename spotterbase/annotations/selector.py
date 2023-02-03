from __future__ import annotations

import abc
from typing import Any, Optional

from spotterbase.annotations.serialization_abc import Portable
from spotterbase.annotations.utils import RdfNodeMixin
from spotterbase.rdf.base import TripleI, BlankNode
from spotterbase.rdf.literals import StringLiteral, NonNegativeIntLiteral
from spotterbase.rdf.vocab import RDF, OA
from spotterbase.sb_vocab import SB


class Selector(Portable, RdfNodeMixin, abc.ABC):
    ...


class SimpleSelector(Selector, abc.ABC):
    """ Simple selectors have a single, continuous range and may be refined by a ListSelector. """
    refinement: Optional[ListSelector]

    @classmethod
    def from_json(cls, json: Any) -> SimpleSelector:
        match json['type']:
            case 'PathSelector':
                return PathSelector.from_json(json)
            case 'OffsetSelector':
                return OffsetSelector.from_json(json)
            case 'ListSelector':
                raise Exception('ListSelector is not a simple selector')
            case other:
                raise Exception(f'Unsupported type for selector: {other}')

    @classmethod
    def _get_refinement_from_json(cls, json: Any) -> Optional[ListSelector]:
        if 'refinedBy' in json:
            return ListSelector.from_json(json['refinedBy'])
        return None


class DiscontinuousSelector(Selector, abc.ABC):
    """ Complex selectors can represent non-continuous ranges and act as a refinement for simple selectors"""


class PathSelector(SimpleSelector):
    def __init__(self, start: str, end: str, refinement: Optional[ListSelector] = None):
        self.start: str = start
        self.end: str = end
        self.refinement: Optional[ListSelector] = refinement

    def to_json(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            'type': 'PathSelector',
            'startPath': self.start,
            'endPath': self.end
        }
        if self.refinement is not None:
            d['refinedBy'] = self.refinement.to_json()
        return d

    @classmethod
    def from_json(cls, json: Any) -> PathSelector:
        assert json['type'] == 'PathSelector'
        return PathSelector(json['startPath'], json['endPath'], cls._get_refinement_from_json(json))

    def to_triples(self) -> TripleI:
        yield self.get_rdf_node(), RDF.type, SB.PathSelector
        yield self.get_rdf_node(), SB.startPath, StringLiteral(self.start)
        yield self.get_rdf_node(), SB.endPath, StringLiteral(self.end)
        if self.refinement is not None:
            yield self.get_rdf_node(), OA.refinedBy, self.refinement.get_rdf_node()
            yield from self.refinement.to_triples()


class OffsetSelector(SimpleSelector):
    def __init__(self, start: int, end: int, refinement: Optional[ListSelector] = None):
        self.start: int = start
        self.end: int = end
        self.refinement: Optional[ListSelector] = refinement

    def to_triples(self) -> TripleI:
        yield self.get_rdf_node(), RDF.type, SB.OffsetSelector
        yield self.get_rdf_node(), OA.start, NonNegativeIntLiteral(self.start)
        yield self.get_rdf_node(), OA.end, NonNegativeIntLiteral(self.end)

    @classmethod
    def from_json(cls, json: Any) -> OffsetSelector:
        assert json['type'] == 'OffsetSelector'
        return OffsetSelector(json['start'], json['end'], cls._get_refinement_from_json(json))

    def to_json(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            'type': 'OffsetSelector',
            'start': self.start,
            'end': self.end
        }
        if self.refinement is not None:
            d['refinedBy'] = self.refinement.to_json()
        return d


class ListSelector(DiscontinuousSelector):
    def __init__(self, selectors: list[SimpleSelector]):
        assert selectors
        self.selectors: list[SimpleSelector] = selectors

    def to_triples(self) -> TripleI:
        yield self.get_rdf_node(), RDF.type, SB.ListSelector
        list_head = BlankNode()
        yield self.get_rdf_node(), RDF.value, list_head
        yield list_head, RDF.first, self.selectors[0].get_rdf_node()
        yield from self.selectors[0].to_triples()

        for selector in self.selectors[1:]:
            new_head = BlankNode()
            yield list_head, RDF.rest, new_head
            list_head = new_head
            yield list_head, RDF.first, selector.get_rdf_node()
            yield from selector.to_triples()

        yield list_head, RDF.rest, RDF.nil

    @classmethod
    def from_json(cls, json: Any) -> ListSelector:
        assert json['type'] == 'ListSelector'
        return ListSelector(selectors=[SimpleSelector.from_json(selector) for selector in json['vals']])

    def to_json(self) -> dict[str, Any]:
        return {
            'type': 'ListSelector',
            'vals': [selector.to_json() for selector in self.selectors]
        }
