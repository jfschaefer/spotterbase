from typing import Optional, Iterable

from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.rdf import Uri
from spotterbase.sparql.endpoint import SparqlEndpoint
from spotterbase.sparql.sb_sparql import get_data_endpoint


def document_iterable_from_query(
        query: str, doc_var: str = 'doc', endpoint: Optional[SparqlEndpoint] = None
) -> Iterable[Document]:
    if endpoint is None:
        endpoint = get_data_endpoint()

    documents: list[Document] = []

    for binding in endpoint.query(query):
        if doc_var in binding:
            doc_uri = binding[doc_var]
            if not isinstance(doc_uri, Uri):
                raise ValueError(f'Variable ?{doc_var} is not a URI: {binding}')
            documents.append(Resolver.get_document_or_fail(doc_uri))
        else:
            raise ValueError(f'Query result does not contain ?{doc_var} variable: {binding}')

    documents.sort(key=lambda d: str(d.get_uri()))
    return documents
