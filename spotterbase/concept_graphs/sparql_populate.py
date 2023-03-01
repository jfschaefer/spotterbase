from __future__ import annotations

import abc
import dataclasses
import logging
from collections import defaultdict
from typing import Iterator, Optional

from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo
from spotterbase.concept_graphs.concept_resolver import ConceptResolver
from spotterbase.rdf.base import Literal, BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF
from spotterbase.sparql.endpoint import SparqlEndpoint

logger = logging.getLogger(__name__)


# TODO: The code is just a prototype and should be heavily refactored and optimized. In particular:
#   * requests should be parallelized (with coroutines or threads)
#   * request sizes should have reasonable limits
#   * results (e.g. for types) should be cached - at least for a single population run

class PropertyPath(abc.ABC):
    """ The needed subset of SPARQL property paths """

    @abc.abstractmethod
    def __truediv__(self, other):
        ...

    @abc.abstractmethod
    def __format__(self, format_spec) -> str:
        ...


@dataclasses.dataclass
class ListPropertyPath(PropertyPath):
    elements: list[PropertyPath]

    def __truediv__(self, other):
        if isinstance(other, Uri):
            return ListPropertyPath(self.elements + [UriPropertyPath(other)])
        elif isinstance(other, ListPropertyPath):
            return ListPropertyPath(self.elements + other.elements)
        elif isinstance(other, PropertyPath):
            return ListPropertyPath(self.elements + [other])
        else:
            raise Exception(f'Unsupported argument type {type(other)}')

    def __format__(self, format_spec) -> str:
        return ' / '.join(format(element, format_spec) for element in self.elements)


@dataclasses.dataclass
class UriPropertyPath(PropertyPath):
    element: Uri
    inverted: bool = False

    def __truediv__(self, other):
        return ListPropertyPath([self]) / other

    def __format__(self, format_spec) -> str:
        if self.inverted:
            return f'^{self.element:<>}'
        else:
            return f'{self.element:<>}'


def get_types(uris: list[Uri], endpoint: SparqlEndpoint, property_path: PropertyPath = UriPropertyPath(RDF.type)) \
        -> dict[Uri, list[Uri]]:
    response = endpoint.query(f'''
SELECT ?uri ?type WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in uris)} }}
    ?uri {property_path} ?type .
}}
    ''')

    results: dict[Uri, list[Uri]] = {uri: [] for uri in uris}
    for line in response:
        type_ = line['type']
        if not isinstance(type_, Uri):
            continue
        uri = line['uri']
        assert isinstance(uri, Uri)  # let's make mypy happy
        results[uri].append(type_)

    return results


def set_plain_attributes(concepts: list[tuple[Concept, Uri]], info: ConceptInfo, property_path: PropertyPath,
                         endpoint: SparqlEndpoint):
    """
        `concepts` is a list of pairs `(concept, root_uri)`, such that `root_uri / property_path` points to `concept`.
    """
    var_count = 0
    var_to_attr: dict[str, AttrInfo] = {}
    lines: list[str] = []
    for attr in info.attrs:
        if attr.can_be_multiple:
            continue
        if attr.target_type is not None:
            continue
        var = f'?v{var_count}'
        var_to_attr[var] = attr
        var_count += 1
        path = property_path / UriPropertyPath(attr.pred_info.uri, inverted=attr.pred_info.is_reversed)
        lines.append(f'OPTIONAL {{ ?uri {path} {var} . }}')

    if not var_to_attr:
        return

    body = '\n'.join(lines)
    concept_by_uri = {uri: concept for concept, uri in concepts}
    response = endpoint.query(f'''
SELECT ?uri {" ".join(var_to_attr.keys())} WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in concept_by_uri)} }}
    {body}
}}
    ''')
    processed: set[Uri] = set()
    for row in response:
        uri = row['uri']
        assert isinstance(uri, Uri)
        if uri in processed:
            logger.warning(f'Multiple results when filling out {uri:<>} / {property_path}')
            continue
        processed.add(uri)
        concept = concept_by_uri[uri]
        for var, a_info in var_to_attr.items():
            if var[1:] not in row:
                continue
            val = row[var[1:]]
            if isinstance(val, Literal):
                if hasattr(concept, a_info.attr_name):
                    logger.warning(f'Concept already has attribute {a_info.attr_name}')
                setattr(concept, a_info.attr_name, val.to_py_val())
            elif isinstance(val, BlankNode):
                logger.warning(f'Got blank node for attribute {a_info.attr_name}'
                               f'for {type(concept)} {uri:<>} / {property_path}. '
                               'Did you forget to set the target_type in the AttrInfo?')
            elif isinstance(val, Uri):
                if hasattr(concept, a_info.attr_name):
                    logger.warning(f'Concept already has attribute {a_info.attr_name}')
                setattr(concept, a_info.attr_name, val)
            else:
                raise TypeError(f'Unexpected type {type(val)}')


class Populator:
    def __init__(self, concept_resolver: ConceptResolver, endpoint: SparqlEndpoint):
        self.concept_resolver: ConceptResolver = concept_resolver
        self.endpoint = endpoint

    def concept_from_types(self, types: list[Uri]) -> Optional[type[Concept]]:
        for type_ in types:
            if type_ in self.concept_resolver:
                return self.concept_resolver[type_]
        return None

    def get_concepts(self, uris: Iterator[Uri]) -> Iterator[Concept]:
        type_info = get_types(list(uris), self.endpoint)
        concepts: list[Concept] = []
        for uri, types in type_info.items():
            concept = self.concept_from_types(types)
            if concept is None:
                logger.warning(f'Cannot infer concept for {uri} from types {types}')
                continue
            concepts.append(concept(uri=uri))
        self.fill_concepts([(concept, concept.uri) for concept in concepts], ListPropertyPath([]))
        yield from concepts

    def fill_concepts(self, concepts: list[tuple[Concept, Uri]], property_path: PropertyPath):
        concepts_by_type: dict[type[Concept], list[tuple[Concept, Uri]]] = defaultdict(list)
        for concept, root_uri in concepts:
            concepts_by_type[type(concept)].append((concept, root_uri))

        for concept_type, concepts_of_that_type in concepts_by_type.items():
            info = concept_type.concept_info
            set_plain_attributes(concepts_of_that_type, info=info, property_path=property_path, endpoint=self.endpoint)
            self._fill_sub_concepts(concept_type, concepts_of_that_type, property_path)

    def _fill_sub_concepts(self, concept_type: type[Concept], concepts: list[tuple[Concept, Uri]],
                           property_path: PropertyPath):
        for attr in concept_type.concept_info.attrs:
            if attr.can_be_multiple:
                continue
            if attr.target_type is None:
                continue
            if len(attr.target_type) > 1:  # TODO
                continue
            sub_concepts: list[tuple[Concept, Uri]] = []
            for concept, root_uri in concepts:
                if hasattr(concept, attr.attr_name):
                    logger.warning(f'Concept already has attribute {attr.attr_name}')
                    continue
                # TODO: set instance uri if it exists
                sub_concept = self.concept_resolver[list(attr.target_type)[0]]()
                setattr(concept, attr.attr_name, sub_concept)
                sub_concepts.append((sub_concept, root_uri))
            self.fill_concepts(sub_concepts,
                               property_path / UriPropertyPath(attr.pred_info.uri, inverted=attr.pred_info.is_reversed))
