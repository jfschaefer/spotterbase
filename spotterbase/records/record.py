from __future__ import annotations

import dataclasses
from typing import Optional, Any, ClassVar

from spotterbase.rdf.literal import Literal
from spotterbase.rdf.types import Subject, Object, TripleI
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF
from spotterbase.sparql.property_path import PropertyPath, UriPath


@dataclasses.dataclass
class PredInfo:
    uri: Uri

    is_rdf_list: bool = False
    literal_type: Optional[Uri] = None
    is_reversed: bool = False  # subject/object are swapped

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


class FieldInfo:
    ...


FieldNoRecord = FieldInfo()  # field is literal or URI (the URI may belong to a record though)
FieldUnknownRecord = FieldInfo()  # field is a record, but we do not know which one


@dataclasses.dataclass
class FieldKnownRecord(FieldInfo):
    record_type: type[Record]


@dataclasses.dataclass
class FieldRecordSet(FieldInfo):
    record_types: set[type[Record]]


@dataclasses.dataclass
class AttrInfo:
    attr_name: str
    pred_info: PredInfo

    field_info: FieldInfo = FieldNoRecord
    multi_field: bool = False
    literal_type: Optional[Uri] = None  # copied from pred_info if not set explicitly

    def __post_init__(self):
        if self.literal_type is None:
            self.literal_type = self.pred_info.literal_type


class RecordInfo:
    record_type: Uri
    is_root_record: bool
    attrs: list[AttrInfo]
    attrs_by_jsonld_term: dict[str, AttrInfo]
    attrs_by_uri: dict[Uri, AttrInfo]
    attrs_by_name: dict[str, AttrInfo]

    def __init__(self, record_type: Uri, attrs: list[AttrInfo], is_root_record: bool = False):
        self.record_type = record_type
        self.attrs: list[AttrInfo] = attrs
        self.is_root_record = is_root_record

        self.attrs_by_jsonld_term = {
            attr.pred_info.json_ld_term: attr for attr in self.attrs if attr.pred_info.json_ld_term
        }
        self.attrs_by_uri = {attr.pred_info.uri: attr for attr in self.attrs}
        self.attrs_by_name = {attr.attr_name: attr for attr in self.attrs}


class RecordMeta(type):
    """ Metaclass for Record. Used for some basic checks. """
    record_info: RecordInfo

    def __init__(self, *args):
        super().__init__(*args)
        if self.__qualname__ == 'Record':
            return
        assert hasattr(self, 'record_info'), f'No record_info provided for {self.__qualname__}'
        assert isinstance(self.record_info, RecordInfo)
        # for a_info in self.record_info.attrs:
        #     assert hasattr(self, a_info.attr_name),\
        #         f'{self.__qualname__} does not have a default value for {a_info.attr_name}'


class Record(metaclass=RecordMeta):
    record_info: ClassVar[RecordInfo]

    # instance attributes (you can overwrite this for root records with uri: Uri)
    uri: Optional[Uri] = None

    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            self.__set_attr(attr, val)

    def require_uri(self) -> Uri:
        assert self.uri is not None
        return self.uri

    def to_triples(self) -> TripleI:
        assert self.uri
        return _record_to_triples(self, self.uri)

    def __set_attr(self, attr: str, val: Optional[Any]):
        assert attr == 'uri' or attr in self.record_info.attrs_by_name
        if val is not None:
            setattr(self, attr, val)

    def check_attrs(self):
        # TODO
        ...


def _record_to_triples(record: Record, node: Subject) -> TripleI:
    yield node, RDF.type, record.record_info.record_type
    for attr in record.record_info.attrs:
        if not hasattr(record, attr.attr_name):
            continue
        attr_val = getattr(record, attr.attr_name)
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
                    assert isinstance(val_node, Uri) or isinstance(val_node, BlankNode), \
                        f'Making a reversed edge would lead to a subject of type {type(val_node)}'
                    yield val_node, p_info.uri, node
                else:
                    yield node, p_info.uri, val_node


def _to_triples(thing) -> tuple[Subject, TripleI]:
    if isinstance(thing, Record):
        node: Subject
        if thing.uri is not None:
            node = thing.uri
        else:
            node = BlankNode()
        return node, _record_to_triples(thing, node)
    elif isinstance(thing, Uri):
        return thing, iter(())
    else:
        raise Exception(f'Unsupported type {type(thing)} of {thing!r}. '
                        'Did you forget to specify the literal type in the attribute info?')
