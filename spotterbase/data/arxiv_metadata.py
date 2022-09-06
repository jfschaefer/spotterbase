import functools
import hashlib

from rdflib import URIRef, Namespace

from spotterbase.config_loader import ConfigFlag

USE_CENTI_ARXIV = ConfigFlag('--centi-arxiv', 'use a subset of arxiv (≈ 1%)')


REL_NAMESPACE = Namespace('http://sigmathling.kwarc.info/arxiv-meta/')
REL_HAS_CATEGORY = REL_NAMESPACE['has-category']
REL_SUBCATEGORY_OF = REL_NAMESPACE['subcategory-of']


class ArxivId:
    uri_namespace = Namespace('https://arxiv.org/abs/')

    def __init__(self, identifier: str):
        self.identifier = identifier

    def as_uri(self) -> URIRef:
        return self.uri_namespace[self.identifier]

    @functools.cache
    def is_in_centi_arxiv(self) -> bool:
        sha256 = hashlib.sha256(self.identifier.encode('utf-8')).hexdigest()
        return int(sha256, base=16) % 100 == 0


class ArxivCategory:
    uri_namespace = Namespace('https://arxiv.org/archive/')

    def __init__(self, category: str):
        self.category = category

    def as_uri(self) -> URIRef:
        return self.uri_namespace[self.category]
