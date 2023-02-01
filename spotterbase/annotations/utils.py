from typing import TypeVar, Optional

from spotterbase.rdf.base import Subject, BlankNode, Uri

_T: TypeVar = TypeVar('_T')


def as_list(arg: _T | list[_T]) -> list[_T]:
    """ If the argument is not a list, it returns a list containing the argument """
    if isinstance(arg, list):
        return arg
    return [arg]


def extract_if_singleton(list_: list[_T]) -> _T | list[_T]:
    """ If the argument is a singleton list, it returns its argument,
        otherwise, it returns the entire list """
    if len(list_) == 1:
        return list_[0]
    return list_


class RdfNodeMixin:
    _rdf_node: Optional[Subject] = None

    def set_rdf_node(self, node: Subject):
        assert self._rdf_node is None, 'node already set'
        self._rdf_node = node

    def has_rdf_uri(self) -> bool:
        return isinstance(self._rdf_node, Uri)

    def get_rdf_node(self) -> Subject:
        """ Gets the RDF node (if none is set, it will set it to a blank node) """
        if self._rdf_node is None:
            self._rdf_node = BlankNode()
        return self._rdf_node
