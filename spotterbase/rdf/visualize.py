from typing import Optional

import graphviz

from spotterbase.rdf import TripleI, Object, Literal, Uri, BlankNode, NameSpaceCollection, StandardNameSpaces


def rdf_node_to_string(
        rdfnode: Object, namespacecollection: Optional[NameSpaceCollection], relaxed_labels: bool
) -> str:
    if isinstance(rdfnode, Literal):
        if relaxed_labels:
            try:
                pyval = rdfnode.to_py_val()
                if type(pyval) in {int, float, bool}:
                    return rdfnode.string
                elif type(pyval) == str:  # noqa
                    return rdfnode.format_string_ntriples()
            except NotImplementedError:
                pass
        return rdfnode.to_turtle()
    elif isinstance(rdfnode, Uri):
        if namespacecollection is not None:
            result = format(namespacecollection.namespacify(rdfnode), ':')
        else:
            result = format(rdfnode, ':')
        # TODO: The following could be improved (e.g. look for separators like /, #, etc.)
        #      also: the turtle escapes of / etc. are annoying
        if relaxed_labels and len(result) > 30:
            split, _, tail = result.rpartition(':')
            if tail:
                result = split + ':' + '...' + tail[-15:]
        return result
    elif isinstance(rdfnode, BlankNode):
        return ''    # don't label blank nodes
    else:
        raise TypeError(f'Unsupported type {type(rdfnode)}')


def triples_to_graphviz(
        triples: TripleI,
        namespacecollection: Optional[NameSpaceCollection] = StandardNameSpaces,
        name: Optional[str] = None,
        relaxed_labels: bool = False,    # if True: some information may not be displayed for compactness
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
            graph.node(
                node_dict[rdfnode],
                label=graphviz.escape(rdf_node_to_string(rdfnode, namespacecollection, relaxed_labels)),
                shape=shape
            )
            nodecounter += 1
        return node_dict[rdfnode]

    for s, p, o in triples:
        graph.edge(get_graphviz_node(s), get_graphviz_node(o),
                   label=graphviz.escape(rdf_node_to_string(p, namespacecollection, relaxed_labels)))
    return graph
