import rdflib

from spotterbase.rdf import TripleI, BlankNode, Uri, Literal


def triples_from_graph(graph: rdflib.Graph) -> TripleI:
    bnode_lookup = {}

    def convert(node: rdflib.term.Node) -> Uri | Literal | BlankNode:
        if isinstance(node, rdflib.BNode):
            if node not in bnode_lookup:
                bnode_lookup[node] = BlankNode()
            return bnode_lookup[node]
        elif isinstance(node, rdflib.URIRef):
            return Uri(node)
        elif isinstance(node, rdflib.Literal):
            return Literal.from_rdflib(node)
        else:
            raise TypeError(f'Unsupported node type {type(node)}')

    for s, p, o in graph:
        yield convert(s), convert(p), convert(o)  # type: ignore
