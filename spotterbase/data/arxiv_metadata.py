import functools
import hashlib
import re

from rdflib import URIRef, Namespace

from spotterbase.config_loader import ConfigFlag

USE_CENTI_ARXIV = ConfigFlag('--centi-arxiv', 'use a subset of arxiv (≈ 1%)')


class ArxivUris:
    topic_system = URIRef('https://arxiv.org/category_taxonomy/')
    corpus = URIRef('https://arxiv.org/')
    centi_arxiv = URIRef('http://sigmathling.kwarc.info/centi-arxiv')


class ArxivId:
    uri_namespace = Namespace('https://arxiv.org/abs/')

    arxiv_id_regex = re.compile(r'^(?P<oldprefix>[a-z-]+/)?(?P<yymm>[0-9]{4})[0-9.]*$')

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other: 'ArxivId') -> bool:
        return self.identifier == other.identifier

    def as_uri(self) -> URIRef:
        return self.uri_namespace[self.identifier]

    @functools.cache
    def is_in_centi_arxiv(self) -> bool:
        sha256 = hashlib.sha256(self.identifier.encode('utf-8')).hexdigest()
        return int(sha256, base=16) % 100 == 0

    @property
    def yymm(self) -> str:
        return self.arxiv_id_regex.match(self.identifier).group('yymm')


class ArxivCategory:
    uri_namespace = Namespace('https://arxiv.org/archive/')

    def __init__(self, category: str):
        self.category = category

    def as_uri(self) -> URIRef:
        return self.uri_namespace[self.category]
