from typing import Optional, Iterable

from spotterbase.concept_graphs.concept_graph import Concept
from spotterbase.rdf.uri import Uri


class ConceptResolver:
    _lookup: dict[Uri, type[Concept]]

    def __init__(self, concepts: Optional[Iterable[type[Concept]]]):
        self._lookup = {}
        if concepts:
            for concept in concepts:
                self.add(concept)

    def __contains__(self, item):
        return item in self._lookup

    def __getitem__(self, item) -> type[Concept]:
        try:
            return self._lookup[item]
        except KeyError:
            raise KeyError(f'Unknown concept type: {item!r}')

    def add(self, concept: type[Concept]):
        type_ = concept.concept_info.concept_type
        if type_ in self._lookup:
            if self._lookup[type_] != concept:
                raise Exception(f'failed to map {type_} to {concept.__qualname__} '
                                f'because it already refers to {self._lookup[type_].__qualname__}')
        self._lookup[type_] = concept
