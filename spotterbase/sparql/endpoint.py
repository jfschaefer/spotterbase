import abc
from typing import Optional, Iterator, Iterable

import requests as requests
from requests.auth import HTTPBasicAuth

from spotterbase.rdf.base import Object
from spotterbase.sparql.query import json_binding_to_object


class SparqlEndpoint(abc.ABC):
    def query(self, query: str) -> Iterable[dict[str, Optional[Object]]]:
        result = self.get(query, accept='application/json')

        for binding in result['results']['bindings']:
            d = {}
            for var in result['head']['vars']:
                if var in binding:
                    d[var] = json_binding_to_object(binding[var])
                else:
                    d[var] = None
            yield d

    def get(self, query: str, accept: str = 'application/json'):
        raise NotImplementedError()

    def post(self, query: str):
        raise NotImplementedError()


class Virtuoso(SparqlEndpoint):
    def __init__(self, endpoint: str = 'http://localhost:8890/sparql'):
        self.endpoint = endpoint

    def get(self, query: str, accept: str = 'application/json'):
        r = requests.get(self.endpoint, params={'query': query},
                         headers={'Accept': accept},
                         auth=HTTPBasicAuth('SPARQL', 'SPARQL'),
                         )
        print(r.text)
        r.raise_for_status()
        if accept == 'application/json':
            return r.json()
        else:
            return r.text

    def post(self, query: str, accept: str = 'application/json'):
        r = requests.post(self.endpoint,
                          headers={'Content-type': 'application/sparql-query', 'Accept': accept},
                          data=query,
                          auth=HTTPBasicAuth('SPARQL', 'SPARQL'))
        r.raise_for_status()
        if accept == 'application/json':
            return r.json()
        else:
            return r.text


def get_endpoint():
    return Virtuoso()
