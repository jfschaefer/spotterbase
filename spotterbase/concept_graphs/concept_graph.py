from __future__ import annotations

import dataclasses
from typing import Optional, Any

from spotterbase.rdf.base import TripleI, Subject, BlankNode, Literal, Object
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF


@dataclasses.dataclass
class PredInfo:
    uri: Uri

    # Info needed for JSON-LD (but might be used for other things as well)
    json_ld_term: Optional[str] = None
    is_rdf_list: bool = False
    literal_type: Optional[Uri] = None


@dataclasses.dataclass
class AttrInfo:
    attr_name: str
    pred_info: PredInfo

    target_type: Optional[set[Uri]] = None
    can_be_multiple: bool = False


class ConceptInfo:
    concept_type: Uri
    is_root_concept: bool
    attrs: list[AttrInfo]
    attrs_by_jsonld_term: dict[str, AttrInfo]
    attrs_by_uri: dict[Uri, AttrInfo]

    def __init__(self, concept_type: Uri, attrs: list[AttrInfo], is_root_concept: bool = False):
        self.concept_type = concept_type
        self.attrs = attrs
        self.is_root_concept = is_root_concept

        self.attrs_by_jsonld_term = {
            attr.pred_info.json_ld_term: attr for attr in self.attrs if attr.pred_info.json_ld_term
        }
        self.attrs_by_uri = {attr.pred_info.uri: attr for attr in self.attrs}


class Concept:
    concept_info: ConceptInfo

    # instance attributes
    uri: Uri

    def to_triples(self) -> TripleI:
        assert self.uri
        return _concept_to_triples(self, self.uri)

    def _set_attr_if_not_none(self, attr: str, val: Optional[Any]):
        if val is not None:
            setattr(self, attr, val)


def _concept_to_triples(concept: Concept, node: Subject) -> TripleI:
    yield node, RDF.type, concept.concept_info.concept_type
    for attr in concept.concept_info.attrs:
        if not hasattr(concept, attr.attr_name):
            continue
        attr_val = getattr(concept, attr.attr_name)
        if attr_val is None:
            continue
        p_info = attr.pred_info

        vals = attr_val if isinstance(attr_val, list) else [attr_val]
        val_nodes: list[Object] = []
        val_node: Object
        for val in vals:
            if p_info.literal_type:
                # TODO: Proper treatment of literals
                val_nodes.append(Literal(str(val), p_info.literal_type))
            else:
                val_node, triples = _to_triples(val)
                yield from triples
                val_nodes.append(val_node)

        if p_info.is_rdf_list:
            list_head = BlankNode()
            yield node, RDF.value, list_head
            yield list_head, RDF.first, val_nodes[0]
            for val_node in val_nodes[1:]:
                new_head = BlankNode()
                yield list_head, RDF.rest, new_head
                list_head = new_head
                yield list_head, RDF.first, val_node
            yield list_head, RDF.rest, RDF.nil
        else:
            for val_node in val_nodes:
                yield node, p_info.uri, val_node


def _to_triples(thing) -> tuple[Subject, TripleI]:
    if isinstance(thing, Concept):
        node: Subject
        if hasattr(thing, 'uri') and thing.uri:
            node = thing.uri
        else:
            node = BlankNode()
        return node, _concept_to_triples(thing, node)
    elif isinstance(thing, Uri):
        return thing, iter(())
    else:
        raise Exception(f'Unsupported type {type(thing)}')
