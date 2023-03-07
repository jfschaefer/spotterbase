from __future__ import annotations

import json
import logging
import urllib.parse
from collections import defaultdict
from typing import Optional, Iterable

import rdflib
import requests as requests
from requests.auth import HTTPBasicAuth

from spotterbase.rdf.base import Object, BlankNode
from spotterbase.sparql.query import json_binding_to_object

logger = logging.getLogger(__name__)


class SparqlEndpoint:
    def query(self, query: str) -> Iterable[dict[str, Optional[Object]]]:
        result = self.send_query(query, accept='application/json')
        bnode_map: defaultdict[str, BlankNode] = defaultdict(BlankNode)
        for binding in result['results']['bindings']:
            d: dict[str, Optional[Object]] = {}
            for var in result['head']['vars']:
                if var in binding:
                    d[var] = json_binding_to_object(binding[var], bnode_map)
                else:
                    d[var] = None
            yield d

    def send_query(self, query: str, accept: str = 'application/json'):
        raise NotImplementedError()

    def update(self, query: str):
        raise NotImplementedError()


class Virtuoso(SparqlEndpoint):
    def __init__(self, endpoint: str = 'http://localhost:8890/sparql'):
        self.endpoint = endpoint

    def send_query(self, query: str, accept: str = 'application/json'):
        if len(urllib.parse.quote_plus(query)) > 10000:
            raise Exception('The query is too long')
        r = requests.get(self.endpoint, params={'query': query},
                         headers={'Accept': accept},
                         auth=HTTPBasicAuth('SPARQL', 'SPARQL'),
                         )
        try:
            r.raise_for_status()
        except Exception as e:
            message = '\n' + r.text
            if len(message) > 2000:
                message = message[:2000] + '...'
            message = message.replace('\n', '\n    ')
            logger.error(f'Response with error code has following message: {message}')
            raise e
        if accept == 'application/json':
            return r.json()
        else:
            return r.text

    def update(self, query: str):
        return self.send_query(query)


class RdflibEndpoint(SparqlEndpoint):
    def __init__(self, graph: Optional[rdflib.Graph] = None):
        # rdflib.ConjunctiveGraph allows named graphs
        self.graph: rdflib.Graph = graph or rdflib.ConjunctiveGraph()

    def send_query(self, query: str, accept: str = 'application/json'):
        results = self.graph.query(query).serialize(format=accept[len('application/'):])
        assert results is not None
        if accept == 'application/json':
            return json.loads(results)
        else:
            return results.decode('utf-8')

    def update(self, query: str):
        if query.lower().strip().startswith('create graph '):  # not supported by rdflib
            return
        return self.graph.update(query)
