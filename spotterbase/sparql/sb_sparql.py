from __future__ import annotations

import argparse
import contextlib
import uuid
from typing import Optional, Iterator

from spotterbase.utils.config_loader import SimpleConfigExtension
from spotterbase.rdf.uri import Uri
from spotterbase.model_core.sb import SB
from spotterbase.sparql.endpoint import SparqlEndpoint, Virtuoso, RdflibEndpoint


def get_tmp_graph_uri() -> Uri:
    return SB.NS['tmp-graph'] / str(uuid.uuid4())


class EndpointConfig(SimpleConfigExtension):
    value: Optional[SparqlEndpoint] = None

    def process_namespace(self, args: argparse.Namespace):
        k = self.name.lstrip('-').replace('-', '_')
        value = getattr(args, k)
        if value is None:
            return
        self.value = eval(value)
        if not isinstance(self.value, SparqlEndpoint):
            raise ValueError(f'{getattr(args, k)} is not a valid SPARQL endpoint')

    def require(self) -> SparqlEndpoint:
        if self.value is None:
            raise Exception(f'No SPARQL endpoint specified (set `{self.name}`)')
        return self.value


# having this list ensures that all endpoints were imported
SUPPORTED_ENDPOINTS: list[type[SparqlEndpoint]] = [Virtuoso, RdflibEndpoint]

WORK_ENDPOINT: EndpointConfig = EndpointConfig(
    '--work-sparql-endpoint',
    'SPARQL endpoint for the internal work of spotterbase (requires write access, i.e. SPARQL updates)',
    default='RdflibEndpoint()'
)
DATA_ENDPOINT: EndpointConfig = EndpointConfig(
    '--data-sparql-endpoint',
    'SPARQL endpoint that stores the generated data (read access may suffice)',
)


def get_work_endpoint() -> SparqlEndpoint:
    return WORK_ENDPOINT.require()


def get_data_endpoint() -> SparqlEndpoint:
    return DATA_ENDPOINT.require()


@contextlib.contextmanager
def tmp_graph(
        data: Optional[Uri | Path] = None, *, endpoint: Optional[SparqlEndpoint] = None
) -> Iterator[tuple[SparqlEndpoint, Uri]]:
    graph_uri = get_tmp_graph_uri()
    data_uri = data if isinstance(data, Uri) else Uri(data.absolute()) if data else None
    endpoint = endpoint or get_work_endpoint()
    try:
        endpoint.update(f'CREATE GRAPH {graph_uri:<>}')
        if data:
            endpoint.update(f'LOAD {data_uri:<>} INTO GRAPH {graph_uri:<>}')
        yield endpoint, graph_uri
    finally:
        endpoint.update(f'DROP GRAPH {graph_uri:<>}')
