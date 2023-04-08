import logging

from spotterbase.model_core.sb import SB
from spotterbase.sparql.sb_sparql import get_data_endpoint

logger = logging.getLogger(__name__)


def main():
    endpoint = get_data_endpoint()
    graph = SB.NS['graph/external']

    logger.info(f'Deleting {graph:<>}')
    endpoint.update(f'CLEAR GRAPH {graph:<>}')

    for uri in ['https://github.com/HajoRijgersberg/OM/raw/master/om-2.0.rdf']:
        logger.info(f'Loading <{uri}>')
        endpoint.update(f'LOAD <{uri}> INTO GRAPH {graph:<>}')


if __name__ == '__main__':
    main()
