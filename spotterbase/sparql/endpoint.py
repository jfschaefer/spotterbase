from __future__ import annotations

import functools
import json
import logging
import urllib.parse
from collections import defaultdict
from typing import Optional, Iterable

import rdflib
import requests as requests
from requests.auth import HTTPBasicAuth

from spotterbase.rdf.types import Object
from spotterbase.rdf.bnode import BlankNode
from spotterbase.sparql.query import json_binding_to_object

logger = logging.getLogger(__name__)


class SparqlEndpoint:
    def query(self, query: str) -> Iterable[dict[str, Optional[Object]]]:
        """ For SELECT queries """
        result = self.send_query(query, accept='application/json')
        bnode_map: defaultdict[str, BlankNode] = defaultdict(BlankNode)
        for binding in result['results']['bindings']:   # SELECT query
            d: dict[str, Optional[Object]] = {}
            for var in result['head']['vars']:
                if var in binding:
                    d[var] = json_binding_to_object(binding[var], bnode_map)
                else:
                    d[var] = None
            yield d

    def ask_query(self, query: str) -> bool:
        result = self.send_query(query, accept='application/json')
        return result['boolean']

    def send_query(self, query: str, accept: str = 'application/json'):
        raise NotImplementedError()

    def update(self, query: str):
        raise NotImplementedError()


class RemoteSparqlEndpoint(SparqlEndpoint):
    def __init__(self, url: str, extra_headers: Optional[dict] = None):
        self.url = url
        self.extra_headers = extra_headers or {}

    def send_query(self, query: str, accept: str = 'application/json'):
        r = requests.get(self.url, params={'query': query},
                         headers={'Accept': accept},
                         **self.extra_headers
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


class Virtuoso(RemoteSparqlEndpoint):
    def __init__(self, url: str = 'http://localhost:8890/sparql'):
        super().__init__(url, {'auth': HTTPBasicAuth('SPARQL', 'SPARQL')})

    def send_query(self, query: str, accept: str = 'application/json'):
        if len(urllib.parse.quote_plus(query)) > 10000:
            raise Exception('The query is too long')   # one of the many quirks Virtuoso has
        return super().send_query(query, accept)

    def update(self, query: str):
        return self.send_query(query)


class RdflibEndpoint(SparqlEndpoint):
    def __init__(self, graph: Optional[rdflib.Graph] = None):
        # rdflib.ConjunctiveGraph allows named graphs
        self.rdflib_version_warn()
        self.graph: rdflib.Graph = graph or rdflib.ConjunctiveGraph()

    def send_query(self, query: str, accept: str = 'application/json'):
        results = self.graph.query(query).serialize(format=accept[len('application/'):])
        assert results is not None
        if accept == 'application/json':
            return json.loads(results)
        else:
            return results.decode('utf-8')

    @staticmethod
    @functools.cache    # only warn once
    def rdflib_version_warn():
        if rdflib.__version__ == '7.0.0':
            logger.warning('rdflib version 7.0.0 has a bug that breaks some SpotterBase functionality. '
                           'It has already been patched (https://github.com/RDFLib/rdflib/pull/2554).')

    def update(self, query: str):
        if query.lower().strip().startswith('create graph '):  # not supported by rdflib
            return
        return self.graph.update(query)


WIKIDATA = RemoteSparqlEndpoint('https://query.wikidata.org/sparql')
