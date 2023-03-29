from typing import Iterator

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
