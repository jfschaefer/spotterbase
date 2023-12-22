from typing import Optional

import graphviz

from spotterbase.rdf import TripleI, Object, Literal, Uri, BlankNode, NameSpaceCollection


def rdf_node_to_string(rdfnode: Object, namespacecollection: Optional[NameSpaceCollection]) -> str:
    if isinstance(rdfnode, Literal):
        return rdfnode.to_turtle()
    elif isinstance(rdfnode, Uri):
        if namespacecollection is not None:
            return format(namespacecollection.namespacify(rdfnode), ':')
        return format(rdfnode, ':')
    elif isinstance(rdfnode, BlankNode):
        return ''    # don't label blank nodes
    else:
        raise TypeError(f'Unsupported type {type(rdfnode)}')


def triples_to_graphviz(
        triples: TripleI,
        namespacecollection: Optional[NameSpaceCollection] = None,
        name: Optional[str] = None
) -> graphviz.Digraph:
    graph = graphviz.Digraph(name=name)
    nodecounter = 0
    node_dict: dict[Object, str] = {}    # rdf node to graphviz node

    def get_graphviz_node(rdfnode: Object) -> str:
        nonlocal nodecounter
        if rdfnode not in node_dict:
            node_dict[rdfnode] = f'node{nodecounter}'
            shape = 'none'
            if isinstance(rdfnode, Literal):
                shape = 'rect'
            elif isinstance(rdfnode, BlankNode):
                shape = 'circle'
            graph.node(node_dict[rdfnode], label=graphviz.escape(rdf_node_to_string(rdfnode, namespacecollection)),
                       shape=shape)
            nodecounter += 1
        return node_dict[rdfnode]

    for s, p, o in triples:
        graph.edge(get_graphviz_node(s), get_graphviz_node(o),
                   label=graphviz.escape(rdf_node_to_string(p, namespacecollection)))
    return graph
