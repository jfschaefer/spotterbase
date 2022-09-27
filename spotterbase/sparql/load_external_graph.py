import logging

from spotterbase.data.rdf import SB
from spotterbase.sparql.endpoint import get_endpoint

logger = logging.getLogger(__name__)

endpoint = get_endpoint()
graph = SB.NS['graph/external']

logger.info(f'Deleting {graph:<>}')
endpoint.post(f'CLEAR GRAPH {graph:<>}')

for uri in ['https://github.com/HajoRijgersberg/OM/raw/master/om-2.0.rdf']:
    logger.info(f'Loading <{uri}>')
    endpoint.post(f'LOAD <{uri}> INTO GRAPH {graph:<>}')
