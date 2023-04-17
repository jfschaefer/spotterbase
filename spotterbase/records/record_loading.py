from typing import Iterator, Iterable

from spotterbase.records.record import Record
from spotterbase.records.sparql_populate import Populator
from spotterbase.rdf.uri import Uri
from spotterbase.sparql.endpoint import SparqlEndpoint


def load_all_records_from_graph(endpoint: SparqlEndpoint, graph: Uri, populator: Populator) -> Iterator[Record]:
    response = endpoint.query(f'''
SELECT DISTINCT ?uri WHERE {{
    GRAPH {graph:<>} {{ ?uri a ?type . }}
    FILTER isIRI(?uri)
}}
    ''')

    def uri_iterator() -> Iterator[Uri]:
        for row in response:
            uri = row['uri']
            assert isinstance(uri, Uri)
            yield uri

    yield from populator.get_records(uris=uri_iterator())


def _get_uris_from_record_vals(vals: list) -> Iterator[Uri]:
    for val in vals:
        if isinstance(val, Uri):
            yield val
        elif isinstance(val, Record):
            yield from _get_uris_from_record(val)


def _get_uris_from_record(record: Record) -> Iterator[Uri]:
    for attr in record.record_info.attrs:
        if not hasattr(record, attr.attr_name):
            continue
        val = getattr(record, attr.attr_name)
        if isinstance(val, list):
            yield from _get_uris_from_record_vals(val)
        else:
            yield from _get_uris_from_record_vals([val])


def load_all_records_transitively(uris: Iterable[Uri], populator: Populator) -> Iterator[Record]:
    processed_uris: set[Uri] = set()
    unprocessed_uris: set[Uri] = set(uris)

    while unprocessed_uris:
        new_records = list(populator.get_records(uris=unprocessed_uris))
        processed_uris.update(unprocessed_uris)
        unprocessed_uris = set()
        for record in new_records:
            yield record

            for uri in _get_uris_from_record(record):
                if uri not in processed_uris:
                    unprocessed_uris.add(uri)
