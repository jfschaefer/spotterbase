from typing import TypeVar, Optional

from lxml.etree import _Element

from spotterbase.rdf.types import Subject
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.uri import Uri

_T = TypeVar('_T')


def as_list(arg: _T | list[_T]) -> list[_T]:
    """ If the argument is not a list, it returns a list containing the argument """
    if isinstance(arg, list):
        return arg
    return [arg]


def get_parent_asserted(node: _Element) -> _Element:
    parent = node.getparent()
    assert parent is not None
    return parent


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
