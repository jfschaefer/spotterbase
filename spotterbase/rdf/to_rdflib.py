""" This module provides a converter for converting to rdflib.

This is largely trivial, but it makes the conversion a more convenient.
It also maintains a state to make sure that a blank node is always mapped
to the same blank node.

Since rdflib.term.Node accepts a value argument, we might
actually be able to do the whole thing without maintaining a state...
"""

from typing import Iterator

import rdflib

from spotterbase.rdf.literal import Literal
from spotterbase.rdf.types import Triple, TripleI
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import RDF, XSD

_rdflib_triple_T = tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]


class Converter:
    bnode_map: dict[BlankNode, rdflib.BNode]

    def __init__(self, suppress_str_datatypes: bool = False):
        self.bnode_map = {}
        self.suppress_str_datatypes = suppress_str_datatypes

    def convert_node(self, node: Uri | Literal | BlankNode) -> rdflib.term.Node:
        match node:
            case BlankNode():
                if node not in self.bnode_map:
                    self.bnode_map[node] = rdflib.BNode()
                return self.bnode_map[node]
            case Uri():
                return node.to_rdflib()
            case Literal():
                # rdflib has problems with using XSD.string as default etc.
                # see e.g. https://github.com/RDFLib/rdflib/issues/2123
                if self.suppress_str_datatypes and node.datatype in {XSD.string, RDF.langString}:
                    rdflib_dt = None
                else:
                    rdflib_dt = str(node.datatype)
                return rdflib.Literal(node.string, lang=node.lang_tag, datatype=rdflib_dt)
            case _:
                raise Exception('cannot support node type ', type(node))

    def convert_triple(self, triple: Triple) -> _rdflib_triple_T:
        # mypy doesn't like something more sophisticated than the following
        return self.convert_node(triple[0]), self.convert_node(triple[1]), self.convert_node(triple[2])

    def convert_triples(self, triples: TripleI) -> Iterator[_rdflib_triple_T]:
        for triple in triples:
            yield self.convert_triple(triple)

    def convert_to_graph(self, triples: TripleI) -> rdflib.Graph:
        graph = rdflib.Graph()
        for triple in self.convert_triples(triples):
            graph.add(triple)
        return graph


def triples_to_graph(triples: TripleI, suppress_str_datatypes: bool = False) -> rdflib.Graph:
    return Converter(suppress_str_datatypes=suppress_str_datatypes).convert_to_graph(triples)
