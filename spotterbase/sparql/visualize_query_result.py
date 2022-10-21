import io
import logging
from pathlib import Path

# no reason to have type stubs installed for libraries used only here
import matplotlib.pyplot as plt  # type: ignore
import networkx as nx            # type: ignore
import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from spotterbase.config_loader import ConfigLoader
from spotterbase.sparql.endpoint import get_endpoint

logger = logging.getLogger(__name__)


def visualize_queryfile(query_file: Path):
    endpoint = get_endpoint()

    with open(query_file, 'r') as fp:
        query = fp.read()
    rdf = endpoint.get(query, accept='application/rdf+xml')
    print(rdf)
    graph = rdflib.Graph()
    graph.parse(io.StringIO(rdf), format='application/rdf+xml')

    networkx_graph = rdflib_to_networkx_multidigraph(graph)
    pos = nx.spring_layout(networkx_graph, scale=2)
    edge_labels = nx.get_edge_attributes(networkx_graph, 'r')
    nx.draw_networkx_edge_labels(networkx_graph, pos, edge_labels=edge_labels)
    nx.draw(networkx_graph, with_labels=True)
    plt.show()


def main():
    config_loader = ConfigLoader()
    config_loader.argparser.add_argument('queryfile', nargs="+")
    args = config_loader.load_from_args()
    for query_file in args.queryfile:
        visualize_queryfile(Path(query_file))
    logger.info('Done')


if __name__ == '__main__':
    main()
