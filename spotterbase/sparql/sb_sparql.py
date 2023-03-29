from __future__ import annotations

import argparse
import uuid
from typing import Optional

from spotterbase.utils.config_loader import SimpleConfigExtension
from spotterbase.rdf.uri import Uri
from spotterbase.anno_core.sb import SB
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
    endpoint = WORK_ENDPOINT.value
    assert endpoint is not None
    return endpoint


def get_data_endpoint() -> SparqlEndpoint:
    endpoint = DATA_ENDPOINT.value
    if endpoint is None:
        raise Exception(f'No SPARQL endpoint specified (set `{DATA_ENDPOINT.name}`)')
    return endpoint
