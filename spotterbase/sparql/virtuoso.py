import requests as requests
from requests.auth import HTTPBasicAuth


class Virtuoso:
    def __init__(self, endpoint: str = 'http://localhost:8890/sparql'):
        self.endpoint = endpoint

    def get(self, query: str):
        r = requests.get(self.endpoint, params={
            'query': query,
            'format': 'application/json', },
            auth=HTTPBasicAuth('spotterbaseuser', 'spotterbasepwd')
        )
         #                 auth=HTTPBasicAuth('dba', 'dba'))
        print(r)
        print(repr(r.text))
        return r.json()

    def post(self, query: str):
        r = requests.post(self.endpoint,
                          headers={'Content-type': 'application/sparql-query'},
                          data=query,
                          auth=HTTPBasicAuth('spotterbaseuser', 'spotterbasepwd'))
        print(r)
        print(r.text)


if __name__ == '__main__':
#     print(Virtuoso().get(
#         '''
# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
# PREFIX oa: <http://www.w3.org/ns/oa#>
#
# PREFIX sb: <http://sigmathling.kwarc.info/spotterbase/>
# # arxiv categories
# PREFIX axc: <https://arxiv.org/archive/>
# # arXMLiv
# PREFIX axm: <http://sigmathling.kwarc.info/arxmliv/>
# # arXMLiv severities
# PREFIX axmsev: <http://sigmathling.kwarc.info/arxmliv/severity/>
# # arMXLiv 2020 release
# PREFIX axm2020: <http://sigmathling.kwarc.info/arxmliv/2020/>
#
# SELECT DISTINCT ?run ?spotter ?version ?date WHERE {
#     ?run a sb:spotterRun .
#     OPTIONAL { ?run sb:withSpotter ?spotter . }
#     OPTIONAL { ?run sb:spotterVersion ?version . }
#     OPTIONAL { ?run sb:runDate ?date . }
# }
#         '''
#     ))
    print(Virtuoso().get('LOAD <file:///drive/spotterbase/centi-arxmliv-substrings-2020.ttl> INTO <http://sigmathling.kwarc.info/spotterbase/arxmliv-subset-graph>'))