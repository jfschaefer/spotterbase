from __future__ import annotations

import logging
from collections import defaultdict
from typing import Iterator, Optional, NewType, Callable, TypeAlias, Iterable

from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo, TargetKnownConcept, \
    TargetNoConcept, TargetUnknownConcept, TargetConceptSet
from spotterbase.concept_graphs.concept_resolver import ConceptResolver
from spotterbase.rdf.base import Literal, BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF
from spotterbase.sparql.endpoint import SparqlEndpoint
from spotterbase.sparql.property_path import PropertyPath, UriPath, SequencePropertyPath

logger = logging.getLogger(__name__)


# TODO: The code is just a prototype and should be heavily optimized. In particular:
#   * requests should be parallelized (with coroutines or threads)
#   * request sizes should have reasonable limits
#   * results (e.g. for types) should be cached - at least for a single population run


# The RootUri of a concept C is the Uri of the root concept that C belongs to.
# The typical use case the following:
#   There is a root concept R has a sub concept C, which we want to populate.
#   C might not have a URI associated with it. So to somehow reference it in SPARQL queries,
#   we instead refer to R's URI (the RootUri of C) and use a property path that leads from R to C.
RootUri = NewType('RootUri', Uri)

SubConcepts: TypeAlias = list[tuple[Concept, RootUri]]
SpecialPopulator: TypeAlias = Callable[[SubConcepts, PropertyPath, 'Populator'], None]


class Populator:
    def __init__(self, concept_resolver: ConceptResolver, endpoint: SparqlEndpoint,
                 special_populators: Optional[dict[type[Concept], list[SpecialPopulator]]] = None,
                 chunk_size: int = 1000):
        self.concept_resolver: ConceptResolver = concept_resolver
        self.endpoint = endpoint
        self.special_populators: dict[type[Concept], list[SpecialPopulator]] = special_populators or {}
        self.chunk_size: int = chunk_size

    def get_concepts(self, uris: Iterable[Uri], warn_if_initial_uri_unresolvable: bool = True) -> Iterator[Concept]:
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
            concepts: list[Concept] = []
            for uri, types in type_info.items():
                concept = self._concept_from_types(types)
                if concept is None:
                    if warn_if_initial_uri_unresolvable:
                        logger.warning(f'Cannot infer concept for {uri} from types {types}')
                    continue
                concepts.append(concept(uri=uri))
            self._fill_concepts([(concept, RootUri(concept.uri)) for concept in concepts], SequencePropertyPath([]))
            yield from concepts

    def _concept_from_types(self, types: list[Uri]) -> Optional[type[Concept]]:
        for type_ in types:
            if type_ in self.concept_resolver:
                return self.concept_resolver[type_]
        return None

    def _fill_concepts(self, concepts: SubConcepts, property_path: PropertyPath):
        concepts_by_type: dict[type[Concept], SubConcepts] = defaultdict(list)
        for concept, root_uri in concepts:
            concepts_by_type[type(concept)].append((concept, root_uri))
        # TODO: fill concept uris if they are not set

        for concept_type, concepts_of_that_type in concepts_by_type.items():
            info = concept_type.concept_info
            # TODO: the following things can be parallelized
            self._set_plain_attributes(concepts_of_that_type, info=info, property_path=property_path)
            self._fill_known_sub_concepts(concept_type, concepts_of_that_type, property_path)
            self._fill_unknown_sub_concepts(concept_type, concepts_of_that_type, property_path)
            self._set_plain_multival_attributes(concepts_of_that_type, info=info, property_path=property_path)
            if concept_type in self.special_populators:
                for populator in self.special_populators[concept_type]:
                    populator(concepts_of_that_type, property_path, self)

    def _fill_known_sub_concepts(self, concept_type: type[Concept], concepts: SubConcepts, property_path: PropertyPath):
        for attr in concept_type.concept_info.attrs:
            if attr.multi_target:
                continue
            if not isinstance(attr.target_type, TargetKnownConcept):
                continue
            sub_concepts: SubConcepts = []
            for concept, root_uri in concepts:
                if hasattr(concept, attr.attr_name):
                    logger.warning(f'Concept already has attribute {attr.attr_name}')
                    continue
                # TODO: set instance uri if it exists
                sub_concept = attr.target_type.concept()
                setattr(concept, attr.attr_name, sub_concept)
                sub_concepts.append((sub_concept, root_uri))
            self._fill_concepts(sub_concepts, property_path / attr.pred_info.to_property_path())

    def _fill_unknown_sub_concepts(self, concept_type: type[Concept], concepts: SubConcepts,
                                   property_path: PropertyPath):
        concept_by_uri: dict[Uri, Concept] = {uri: concept for concept, uri in concepts}
        for attr in concept_type.concept_info.attrs:
            if attr.multi_target:
                continue
            if not (attr.target_type == TargetUnknownConcept or isinstance(attr.target_type, TargetConceptSet)):
                # for simplicity, we ignore the set of possible target concepts if we have one
                continue

            # step 1: get target types
            types_ = self._get_types(concept_by_uri.keys(),
                                     property_path / attr.pred_info.to_property_path() / RDF.type)
            # step 2: instantiate sub-concepts according to type
            sub_concepts: SubConcepts = []
            for uri in types_:
                concept = concept_by_uri[uri]
                if hasattr(concept, attr.attr_name):
                    logger.warning(f'Concept already has attribute {attr.attr_name}')
                    continue
                sub_concept_type = self._concept_from_types(types_[uri])
                if sub_concept_type is None:
                    logger.warning(f'Cannot find concept for types {types_[uri]} '
                                   '(did you forget to add it to the resolver? (ignoring attribute)')
                    continue
                # TODO: set sub_concept.uri (maybe this should be the task of _fill_concepts)
                sub_concept = sub_concept_type()
                setattr(concept, attr.attr_name, sub_concept)
                sub_concepts.append((sub_concept, RootUri(uri)))
            # step 3: recursively fill up concepts
            self._fill_concepts(sub_concepts, property_path / attr.pred_info.to_property_path())

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

    def _set_plain_attributes(self, concepts: SubConcepts, info: ConceptInfo, property_path: PropertyPath):
        """ Fills in all attributes where a single plain value (literal or URI) is expected. """

        # Step 1: Prepare query content
        var_to_attr: dict[str, AttrInfo] = {}
        lines: list[str] = []
        for attr in info.attrs:
            if attr.multi_target:
                # note: requires a separate query for each multi-target to avoid exponential blow-up of response
                continue
            if attr.target_type != TargetNoConcept:
                continue
            var = f'?v{len(var_to_attr)}'
            var_to_attr[var] = attr
            path = property_path / attr.pred_info.to_property_path()
            lines.append(f'OPTIONAL {{ ?uri {path.to_string()} {var} . }}')

        if not var_to_attr:
            return

        # Step 2: Assemble and send query
        body = '    \n'.join(lines)
        concept_by_uri: dict[Uri, Concept] = {uri: concept for concept, uri in concepts}
        response = self.endpoint.query(f'''
SELECT DISTINCT ?uri {" ".join(var_to_attr.keys())} WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in concept_by_uri)} }}
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
            concept = concept_by_uri[uri]
            for var, a_info in var_to_attr.items():
                if var[1:] not in row:
                    continue
                val = row[var[1:]]
                if val is None:
                    continue
                if hasattr(concept, a_info.attr_name):
                    logger.warning(f'Concept already has attribute {a_info.attr_name}')
                if isinstance(val, Literal):
                    setattr(concept, a_info.attr_name, val.to_py_val())
                elif isinstance(val, BlankNode):
                    logger.warning(f'Got blank node for attribute {a_info.attr_name} '
                                   f'for {type(concept)} {uri:<>} / {property_path}. '
                                   'Did you forget to set the target_type in the AttrInfo?')
                elif isinstance(val, Uri):
                    setattr(concept, a_info.attr_name, val)
                else:
                    raise TypeError(f'Unexpected type {type(val)} for attribute {a_info.attr_name} '
                                    f'of concept {type(concept)}')

    def _set_plain_multival_attributes(self, concepts: SubConcepts, info: ConceptInfo, property_path: PropertyPath):
        """ Fills in attributes that can have multiple plain values (Uris or literals) """
        for attr in info.attrs:  # TODO: this loop could be parallelized
            if not attr.multi_target:
                continue
            if attr.target_type != TargetNoConcept:
                continue
            path = property_path / attr.pred_info.to_property_path()
            for concept, _ in concepts:
                if hasattr(concept, attr.attr_name):
                    logger.warning(f'Concept already has attribute {attr.attr_name} (overwriting it)')
                setattr(concept, attr.attr_name, [])

            concept_by_uri: dict[Uri, Concept] = {uri: concept for concept, uri in concepts}
            response = self.endpoint.query(f'''
SELECT ?uri ?val WHERE {{
    VALUES ?uri {{ {" ".join(format(uri, '<>') for uri in concept_by_uri)} }}
    ?uri {path.to_string()} ?val .
}}
        '''.strip())

            for row in response:
                uri = row['uri']
                assert isinstance(uri, Uri)
                concept = concept_by_uri[uri]
                val = row['val']
                if isinstance(val, Literal):
                    getattr(concept, attr.attr_name).append(val.to_py_val())
                elif isinstance(val, Uri):
                    getattr(concept, attr.attr_name).append(val)
                elif isinstance(val, BlankNode):
                    logger.warning(
                        f'Got blank node for multi-value attribute {attr.attr_name} for concept {type(concept)}. '
                        'Did you forget to set the target_type in AttrInfo?')
                else:
                    raise TypeError(f'Unexpected type {type(val)}')
