from typing import Iterator

from spotterbase.concept_graphs.concept_graph import Concept
from spotterbase.concept_graphs.sparql_populate import Populator
from spotterbase.rdf.uri import Uri
from spotterbase.sparql.endpoint import SparqlEndpoint


# class ConceptLoader(abc.ABC):
#     populator: Populator
#
#     def __init__(self, populator: Populator):
#         self.populator = populator


def load_all_concepts_from_graph(endpoint: SparqlEndpoint, graph: Uri, populator: Populator) -> Iterator[Concept]:
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

    yield from populator.get_concepts(uris=uri_iterator())
