from __future__ import annotations

import logging
from collections import defaultdict
from typing import Iterator, Optional, NewType, Callable, TypeAlias, Iterable

from spotterbase.records.record import Record, RecordInfo, AttrInfo, FieldKnownRecord, \
    FieldNoRecord, FieldUnknownRecord, FieldRecordSet
from spotterbase.records.record_class_resolver import RecordClassResolver
from spotterbase.rdf.literal import Literal
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF
from spotterbase.sparql.endpoint import SparqlEndpoint
from spotterbase.sparql.property_path import PropertyPath, UriPath, SequencePropertyPath

logger = logging.getLogger(__name__)


# TODO: The code is just a prototype and should be heavily optimized. In particular:
#   * requests should be parallelized (with coroutines or threads)
#   * request sizes should have reasonable limits
#   * results (e.g. for types) should be cached - at least for a single population run


# The RootUri of a record C is the Uri of the root record that C belongs to.
# The typical use case the following:
#   There is a root record R has a sub record C, which we want to populate.
#   C might not have a URI associated with it. So to somehow reference it in SPARQL queries,
#   we instead refer to R's URI (the RootUri of C) and use a property path that leads from R to C.
RootUri = NewType('RootUri', Uri)

SubRecords: TypeAlias = list[tuple[Record, RootUri]]
SpecialPopulator: TypeAlias = Callable[[SubRecords, PropertyPath, 'Populator'], None]


class Populator:
    def __init__(self, record_type_resolver: RecordClassResolver, endpoint: SparqlEndpoint,
                 special_populators: Optional[dict[type[Record], list[SpecialPopulator]]] = None,
                 chunk_size: int = 1000):
        self.record_type_resolver: RecordClassResolver = record_type_resolver
        self.endpoint = endpoint
        self.special_populators: dict[type[Record], list[SpecialPopulator]] = special_populators or {}
        self.chunk_size: int = chunk_size

    def get_records(self, uris: Iterable[Uri], warn_if_initial_uri_unresolvable: bool = True) -> Iterator[Record]:
        uris_iterator = iter(uris)
        while True:
            chunk: list[Uri] = []
            for uri in uris_iterator:
                chunk.append(uri)
                if len(chunk) >= self.chunk_size:
                    break
            if not chunk:   # done
                return

            type_info = self._get_types(list(chunk))
            records: list[Record] = []
            for uri, types in type_info.items():
                record_type = self._record_type_from_uris(types)
                if record_type is None:
                    if warn_if_initial_uri_unresolvable:
                        logger.warning(f'Cannot infer record type for {uri} from types {types}')
                    continue
                records.append(record_type(uri=uri))

            self._fill_records([(record, RootUri(record.require_uri())) for record in records],
                               SequencePropertyPath([]))
            yield from records

    def _record_type_from_uris(self, types: list[Uri]) -> Optional[type[Record]]:
        for type_ in types:
            if type_ in self.record_type_resolver:
                return self.record_type_resolver[type_]
        return None

    def _fill_records(self, records: SubRecords, property_path: PropertyPath):
        records_by_type: dict[type[Record], SubRecords] = defaultdict(list)
        for record, root_uri in records:
            records_by_type[type(record)].append((record, root_uri))
        # TODO: fill record uris if they are not set

        for record_type, records_of_that_type in records_by_type.items():
            info = record_type.record_info
            # TODO: the following things can be parallelized
            self._set_plain_attributes(records_of_that_type, info=info, property_path=property_path)
            self._fill_known_sub_records(record_type, records_of_that_type, property_path)
            self._fill_unknown_sub_records(record_type, records_of_that_type, property_path)
            self._set_plain_multival_attributes(records_of_that_type, info=info, property_path=property_path)
            if record_type in self.special_populators:
                for populator in self.special_populators[record_type]:
                    populator(records_of_that_type, property_path, self)

    def _fill_known_sub_records(self, record_type: type[Record], records: SubRecords, property_path: PropertyPath):
        for attr in record_type.record_info.attrs:
            if attr.multi_field:
                continue
            if not isinstance(attr.field_info, FieldKnownRecord):
                continue
            sub_records: SubRecords = []
            for record, root_uri in records:
                if hasattr(record, attr.attr_name):
                    logger.warning(f'Record already has attribute {attr.attr_name}')
                    continue
                # TODO: set instance uri if it exists
                sub_record = attr.field_info.record_type()
                setattr(record, attr.attr_name, sub_record)
                sub_records.append((sub_record, root_uri))
            self._fill_records(sub_records, property_path / attr.pred_info.to_property_path())

    def _fill_unknown_sub_records(self, record_type: type[Record], records: SubRecords,
                                  property_path: PropertyPath):
        record_by_uri: dict[Uri, Record] = {uri: record for record, uri in records}
        for attr in record_type.record_info.attrs:
            if attr.multi_field:
                continue
            if not (attr.field_info == FieldUnknownRecord or isinstance(attr.field_info, FieldRecordSet)):
                # for simplicity, we ignore the set of possible target records if we have one
                continue

            # step 1: get field types
            types_ = self._get_types(record_by_uri.keys(),
                                     property_path / attr.pred_info.to_property_path() / RDF.type)
            # step 2: instantiate sub-records according to type
            sub_records: SubRecords = []
            for uri in types_:
                record = record_by_uri[uri]
                if hasattr(record, attr.attr_name):
                    logger.warning(f'Record already has attribute {attr.attr_name}')
                    continue
                sub_record_type = self._record_type_from_uris(types_[uri])
                if sub_record_type is None:
                    logger.warning(f'Cannot find record for types {types_[uri]} '
                                   '(did you forget to add it to the resolver? (ignoring attribute)')
                    continue
                # TODO: set sub_record.uri (maybe this should be the task of _fill_records)
                sub_record = sub_record_type()
                setattr(record, attr.attr_name, sub_record)
                sub_records.append((sub_record, RootUri(uri)))
            # step 3: recursively fill up records
            self._fill_records(sub_records, property_path / attr.pred_info.to_property_path())

    def _get_types(self, uris: Iterable[Uri], property_path: PropertyPath = UriPath(RDF.type)) \
            -> dict[Uri, list[Uri]]:
        response = self.endpoint.query(f'''
SELECT ?uri ?type WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in uris)} }}
    ?uri {property_path.to_string()} ?type .
}}
        '''.strip())

        results: dict[Uri, list[Uri]] = {uri: [] for uri in uris}
        for line in response:
            type_ = line['type']
            if not isinstance(type_, Uri):
                continue
            uri = line['uri']
            assert isinstance(uri, Uri)  # let's make mypy happy
            results[uri].append(type_)

        return results

    def _set_plain_attributes(self, records: SubRecords, info: RecordInfo, property_path: PropertyPath):
        """ Fills in all attributes where a single plain value (literal or URI) is expected. """

        # Step 1: Prepare query content
        var_to_attr: dict[str, AttrInfo] = {}
        lines: list[str] = []
        for attr in info.attrs:
            if attr.multi_field:
                # note: requires a separate query for each multi-field to avoid exponential blow-up of response
                continue
            if attr.field_info != FieldNoRecord:
                continue
            var = f'?v{len(var_to_attr)}'
            var_to_attr[var] = attr
            path = property_path / attr.pred_info.to_property_path()
            lines.append(f'OPTIONAL {{ ?uri {path.to_string()} {var} . }}')

        if not var_to_attr:
            return

        # Step 2: Assemble and send query
        body = '    \n'.join(lines)
        record_by_uri: dict[Uri, Record] = {uri: record for record, uri in records}
        response = self.endpoint.query(f'''
SELECT DISTINCT ?uri {" ".join(var_to_attr.keys())} WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in record_by_uri)} }}
    {body}
}}
        '''.strip())

        # Step 3: Process query results
        processed: set[Uri] = set()
        for row in response:
            uri = row['uri']
            assert isinstance(uri, Uri)
            if uri in processed:
                logger.warning(f'Multiple results when filling out {uri:<>} {property_path}')
                continue
            processed.add(uri)
            record = record_by_uri[uri]
            for var, a_info in var_to_attr.items():
                if var[1:] not in row:
                    continue
                val = row[var[1:]]
                if val is None:
                    continue
                if hasattr(record, a_info.attr_name):
                    logger.warning(f'Record already has attribute {a_info.attr_name}')
                if isinstance(val, Literal):
                    setattr(record, a_info.attr_name, val.to_py_val())
                elif isinstance(val, BlankNode):
                    logger.warning(f'Got blank node for attribute {a_info.attr_name} '
                                   f'for {type(record)} {uri:<>} / {property_path}. '
                                   'Did you forget to set the field_info in the AttrInfo?')
                elif isinstance(val, Uri):
                    setattr(record, a_info.attr_name, val)
                else:
                    raise TypeError(f'Unexpected type {type(val)} for attribute {a_info.attr_name} '
                                    f'of record {type(record)}')

    def _set_plain_multival_attributes(self, records: SubRecords, info: RecordInfo, property_path: PropertyPath):
        """ Fills in attributes that can have multiple plain values (Uris or literals) """
        for attr in info.attrs:  # TODO: this loop could be parallelized
            if not attr.multi_field:
                continue
            if attr.field_info != FieldNoRecord:
                continue
            path = property_path / attr.pred_info.to_property_path()
            for record, _ in records:
                if hasattr(record, attr.attr_name):
                    logger.warning(f'Record already has attribute {attr.attr_name} (overwriting it)')
                setattr(record, attr.attr_name, [])

            record_by_uri: dict[Uri, Record] = {uri: record for record, uri in records}
            response = self.endpoint.query(f'''
SELECT ?uri ?val WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in record_by_uri)} }}
    ?uri {path.to_string()} ?val .
}}
        '''.strip())

            for row in response:
                uri = row['uri']
                assert isinstance(uri, Uri)
                record = record_by_uri[uri]
                val = row['val']
                if isinstance(val, Literal):
                    getattr(record, attr.attr_name).append(val.to_py_val())
                elif isinstance(val, Uri):
                    getattr(record, attr.attr_name).append(val)
                elif isinstance(val, BlankNode):
                    logger.warning(
                        f'Got blank node for multi-value attribute {attr.attr_name} for record {type(record)}. '
                        'Did you forget to set the field_info in AttrInfo?')
                else:
                    raise TypeError(f'Unexpected type {type(val)}')
