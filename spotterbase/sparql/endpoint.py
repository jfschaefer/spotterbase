import abc

import requests as requests
from requests.auth import HTTPBasicAuth


class SparqlEndpoint(abc.ABC):
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
        r.raise_for_status()
        if accept == 'application/json':
            return r.json()
        else:
            return r.text

    def post(self, query: str):
        r = requests.post(self.endpoint,
                          headers={'Content-type': 'application/sparql-query'},
                          data=query,
                          auth=HTTPBasicAuth('SPARQL', 'SPARQL'))
        r.raise_for_status()


def get_endpoint():
    return Virtuoso()
