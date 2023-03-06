from __future__ import annotations

import dataclasses
from typing import Optional, Any

from spotterbase.rdf.base import TripleI, Subject, BlankNode, Literal, Object
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF
from spotterbase.sparql.property_path import PropertyPath, UriPath


@dataclasses.dataclass
class PredInfo:
    uri: Uri

    is_rdf_list: bool = False
    literal_type: Optional[Uri] = None
    is_reversed: bool = False    # subject/object are swapped

    # Info needed for JSON-LD (but might be used for other things as well)
    json_ld_term: Optional[str] = None
    json_ld_type_is_id: bool = False

    def __post_init__(self):
        if self.json_ld_type_is_id:
            assert self.json_ld_term, 'json_ld_term must be set if the type is "@id"'
            assert self.literal_type is None, 'cannot have literal type if the type is "@id"'
        if self.is_reversed:
            assert not self.is_rdf_list, 'cannot have reversed predicate for RDF list'
            assert not self.literal_type, 'cannot have reversed predicate for literals'

    def to_property_path(self) -> PropertyPath:
        prop_path: PropertyPath = UriPath(self.uri)
        if self.is_reversed:
            prop_path = prop_path.inverted()
        return prop_path


class TargetConceptInfo:
    ...


TargetNoConcept = TargetConceptInfo()   # target is literal or URI (the URI may belong to a concept though)
TargetUnknownConcept = TargetConceptInfo()   # target is a concept, but we do not know which one


@dataclasses.dataclass
class TargetKnownConcept(TargetConceptInfo):
    concept: type[Concept]


@dataclasses.dataclass
class TargetConceptSet(TargetConceptInfo):
    concepts: set[type[Concept]]


@dataclasses.dataclass
class AttrInfo:
    attr_name: str
    pred_info: PredInfo

    target_type: TargetConceptInfo = TargetNoConcept
    multi_target: bool = False
    literal_type: Optional[Uri] = None      # copied from pred_info if not set explicitly

    def __post_init__(self):
        if self.literal_type is None:
            self.literal_type = self.pred_info.literal_type


class ConceptInfo:
    concept_type: Uri
    is_root_concept: bool
    attrs: list[AttrInfo]
    attrs_by_jsonld_term: dict[str, AttrInfo]
    attrs_by_uri: dict[Uri, AttrInfo]

    def __init__(self, concept_type: Uri, attrs: list[AttrInfo], is_root_concept: bool = False):
        self.concept_type = concept_type
        self.attrs: list[AttrInfo] = attrs
        self.is_root_concept = is_root_concept

        self.attrs_by_jsonld_term = {
            attr.pred_info.json_ld_term: attr for attr in self.attrs if attr.pred_info.json_ld_term
        }
        self.attrs_by_uri = {attr.pred_info.uri: attr for attr in self.attrs}


class Concept:
    concept_info: ConceptInfo

    # instance attributes
    uri: Uri

    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            self._set_attr_if_not_none(attr, val)

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
            if attr.literal_type:
                val_nodes.append(Literal.from_py_val(val, attr.literal_type))
            else:
                val_node, triples = _to_triples(val)
                yield from triples
                val_nodes.append(val_node)

        if p_info.is_rdf_list:
            assert not p_info.is_reversed
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
                if p_info.is_reversed:
                    assert isinstance(val_node, Uri) or isinstance(val_node, BlankNode),\
                        f'Making a reversed edge would lead to a subject of type {type(val_node)}'
                    yield val_node, p_info.uri, node
                else:
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
        raise Exception(f'Unsupported type {type(thing)} of {thing!r}. '
                        'Did you forget to specify the literal type in the attribute info?')
