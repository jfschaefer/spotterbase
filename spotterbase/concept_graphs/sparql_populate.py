# TODO: The code just a prototype and should be heavily optimized. In particular:
#   * requests should be parallelized (with coroutines or threads)
#   * request sizes should have reasonable limits
#   * results (e.g. for types) should be cached - at least for a single population run
import logging
from typing import Iterator

from spotterbase.concept_graphs.concept_graph import Concept
from spotterbase.concept_graphs.concept_resolver import ConceptResolver
from spotterbase.rdf.uri import Uri
from spotterbase.sparql.endpoint import SparqlEndpoint

logger = logging.getLogger(__name__)


def get_types(uris: list[Uri], endpoint: SparqlEndpoint) -> dict[Uri, list[Uri]]:
    response = endpoint.query(f'''
SELECT ?uri ?type WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in uris)} }}
    ?uri a ?type .
}}
    ''')

    results: dict[Uri, list[Uri]] = {uri: [] for uri in uris}
    for line in response:
        type_ = line['type']
        if not isinstance(type_, Uri):
            continue
        uri = line['uri']
        assert isinstance(uri, Uri)   # let's make mypy happy
        results[uri].append(type_)

    return results


class Populator:
    def __init__(self, concept_resolver: ConceptResolver, endpoint: SparqlEndpoint):
        self.concept_resolver: ConceptResolver = concept_resolver
        self.endpoint = endpoint

    def get_concepts(self, uris: Iterator[Uri]) -> Iterator[Concept]:
        type_info = get_types(list(uris), self.endpoint)
        concepts: list[Concept] = []
        for uri, types in type_info.items():
            for type_ in types:
                if type_ in self.concept_resolver:
                    concepts.append(self.concept_resolver[type_](uri=uri))
                    continue
                logger.warning(f'Cannot infer concept for {uri} from types {types}')

        yield from concepts
