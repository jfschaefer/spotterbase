from __future__ import annotations

import logging
from collections import defaultdict
from typing import Optional

from spotterbase.anno_core.selector import PathSelector, OffsetSelector, ListSelector
from spotterbase.records.record import Record, RecordInfo, AttrInfo, FieldRecordSet
from spotterbase.records.oa_support import OA_PRED
from spotterbase.records.sparql_populate import SubRecords, Populator
from spotterbase.rdf.literal import Literal
from spotterbase.rdf.types import Subject
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF
from spotterbase.anno_core.sb import SB, SB_PRED
from spotterbase.sparql.property_path import PropertyPath, UriPath

logger = logging.getLogger(__name__)


class FragmentTarget(Record):
    record_info = RecordInfo(
        record_type=SB.FragmentTarget,
        attrs=[
            AttrInfo('source', OA_PRED.source),
            AttrInfo('selectors', OA_PRED.selector, multi_field=True,
                     field_info=FieldRecordSet({OffsetSelector, PathSelector})),
        ],
        is_root_record=True,
    )

    # attributes
    source: Uri
    selectors: list[PathSelector | OffsetSelector]

    def __init__(self, uri: Optional[Uri] = None, source: Optional[Uri] = None,
                 selectors: Optional[list] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('source', source)
        self._set_attr_if_not_none('selectors', selectors)


def _populate_without_refinements(fragment_targets: SubRecords, property_path: PropertyPath, populator: Populator):
    uri_to_record: dict[Uri, FragmentTarget] = {}
    fragment_targets = fragment_targets
    for record, root_uri in fragment_targets:
        assert isinstance(record, FragmentTarget)
        if hasattr(record, 'selectors') and record.selectors:
            logger.warning(f'{record.uri} already has selectors. Overwriting them.')
        record.selectors = []
        uri_to_record[root_uri] = record

    for record_class, record_type_uri, start_pred, end_pred in [
        (PathSelector, SB.PathSelector, SB_PRED.startPath, SB_PRED.endPath),
        (OffsetSelector, SB.OffsetSelector, OA_PRED.start, OA_PRED.end),
    ]:

        results = populator.endpoint.query(f'''
SELECT ?uri ?selector ?start ?end WHERE {{
    VALUES ?uri {{ {" ".join(f'{uri:<>}' for uri in uri_to_record)} }}
    ?uri {(property_path / OA_PRED.selector.to_property_path()).to_string()} ?selector .
    ?selector a {record_type_uri:<>} .
    ?selector {start_pred.to_property_path().to_string()} ?start .
    ?selector {end_pred.to_property_path().to_string()} ?end .
}}
        ''')

        for row in results:
            uri = row['uri']
            assert isinstance(uri, Uri)
            record = uri_to_record[uri]
            if any(isinstance(selector, record_class) for selector in record.selectors):
                raise Exception(f'Received multiple {record_class.__name__} (or start/end points) for a target')
            start, end = row['start'], row['end']
            assert isinstance(start, Literal) and isinstance(end, Literal)
            record.selectors.append(record_class(start=start.to_py_val(), end=end.to_py_val()))


def _populate_refinements(fragment_targets: SubRecords, property_path: PropertyPath, populator: Populator):
    uri_to_record: dict[Uri, FragmentTarget] = {}
    for record, root_uri in fragment_targets:
        assert isinstance(record, FragmentTarget)
        uri_to_record[root_uri] = record

    for record_class, record_type, start_pred, end_pred in [
        (PathSelector, SB.PathSelector, SB_PRED.startPath, SB_PRED.endPath),
        (OffsetSelector, SB.OffsetSelector, OA_PRED.start, OA_PRED.end),
    ]:
        results = populator.endpoint.query(f'''
SELECT ?uri ?entry ?nextentry ?start ?end WHERE {{
    VALUES ?uri {{ {" ".join(f'{uri:<>}' for uri in uri_to_record)} }}
    ?uri {(property_path / OA_PRED.selector.to_property_path()).to_string()} ?selector .
    ?selector a {record_type:<>} .
    ?selector {OA_PRED.refinedBy.to_property_path().to_string()} ?listselector .
    ?listselector a {SB.ListSelector:<>} .
    ?listselector {(SB_PRED.vals.to_property_path() / UriPath(RDF.rest).with_star()).to_string()} ?entry .
    ?entry {RDF.rest:<>} ?nextentry .
    ?entry {RDF.first:<>} ?subselector .
    ?subselector a {record_type:<>} .
    ?subselector {start_pred.to_property_path().to_string()} ?start .
    ?subselector {end_pred.to_property_path().to_string()} ?end .
}}
        ''')

        # results have to be combined to get the order of the selectors right
        aggregator: dict[Uri, dict[Subject, tuple[PathSelector | OffsetSelector, Subject]]] = defaultdict(dict)
        # The contained dictionaries map a list node L_i to the node L_{i-1}/rdf:first and the node L_{i-1}.
        # That allows us to reconstruct the list backwards, starting with rdf:nil.
        for row in results:
            uri = row['uri']
            assert isinstance(uri, Uri)
            entry, next_entry = row['entry'], row['nextentry']
            assert isinstance(entry, BlankNode)
            assert isinstance(next_entry, BlankNode) or isinstance(next_entry, Uri) and next_entry == RDF.nil
            start, end = row['start'], row['end']
            assert isinstance(start, Literal) and isinstance(end, Literal)
            aggregator[uri][next_entry] = (
                record_class(start=start.to_py_val(), end=end.to_py_val()),
                entry,
            )

        for uri, list_data in aggregator.items():
            record = uri_to_record[uri]
            parent_selector = [selector for selector in record.selectors if isinstance(selector, record_class)][0]
            selectors = []
            tail: Subject = RDF.nil
            while tail in list_data:
                selector, tail = list_data[tail]
                selectors.append(selector)
            parent_selector.refinement = ListSelector(selectors=list(reversed(selectors)))


def populate_standard_selectors(fragment_targets: SubRecords, property_path: PropertyPath, populator: Populator):
    _populate_without_refinements(fragment_targets, property_path, populator)
    _populate_refinements(fragment_targets, property_path, populator)
