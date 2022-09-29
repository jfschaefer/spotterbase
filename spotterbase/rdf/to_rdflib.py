from typing import Iterator

import rdflib

from spotterbase.rdf.base import TripleI, BlankNode, Triple, Uri, Literal
from spotterbase.rdf.vocab import RDF, XSD

_rdflib_triple_T = tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]


class Converter:
    bnode_map: dict[BlankNode, rdflib.BNode] = {}

    @classmethod
    def convert_node(cls, node: Uri | Literal | BlankNode) -> rdflib.term.Node:
        match node:
            case BlankNode():
                if node not in cls.bnode_map:
                    cls.bnode_map[node] = rdflib.BNode()
                return cls.bnode_map[node]
            case Uri():
                return rdflib.URIRef(node.full_uri())
            case Literal():
                # rdflib has problems with using XSD.string as default etc.
                # see e.g. https://github.com/RDFLib/rdflib/issues/2123
                rdflib_dt = node.datatype.full_uri() if node.datatype not in {XSD.string, RDF.langString} else None
                return rdflib.Literal(node.string, lang=node.lang_tag, datatype=rdflib_dt)

    @classmethod
    def convert_triple(cls, triple: Triple) -> _rdflib_triple_T:
        # mypy doesn't like something more sophisticated than the following
        return cls.convert_node(triple[0]), cls.convert_node(triple[1]), cls.convert_node(triple[2])

    @classmethod
    def convert_triples(cls, triples: TripleI) -> Iterator[_rdflib_triple_T]:
        for triple in triples:
            yield cls.convert_triple(triple)

    @classmethod
    def convert_to_graph(cls, triples: TripleI) -> rdflib.Graph:
        graph = rdflib.Graph()
        for triple in cls.convert_triples(triples):
            graph.add(triple)
        return graph
