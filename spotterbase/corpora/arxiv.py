import functools
import hashlib
import re

from spotterbase.config_loader import ConfigFlag
from spotterbase.sb_vocab import SB
from spotterbase.rdf.base import Uri, NameSpace

USE_CENTI_ARXIV = ConfigFlag('--centi-arxiv', 'use a subset of arxiv (≈ 1 percent)')


class InvalidArxivId(Exception):
    pass


class ArxivId:
    arxiv_id_regex = re.compile(r'^(?P<oldprefix>[a-z-]+/)?(?P<yymm>[0-9]{4})[0-9.]*$')

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other) -> bool:
        match other:
            case ArxivId():
                return self.identifier == other.identifier
            case str():
                return self.identifier == other
            case _:
                return NotImplemented

    def as_uri(self) -> Uri:
        return ArxivUris.arxiv_id[self.identifier]

    @functools.cache
    def is_in_centi_arxiv(self) -> bool:
        sha256 = hashlib.sha256(self.identifier.encode('utf-8')).hexdigest()
        return int(sha256, base=16) % 100 == 0

    @property
    def yymm(self) -> str:
        if match := self.arxiv_id_regex.match(self.identifier):
            return match.group('yymm')
        raise InvalidArxivId(self.arxiv_id_regex)


class ArxivCategory:
    def __init__(self, category: str):
        self.category = category

    def as_uri(self) -> Uri:
        return ArxivUris.arxiv_cat[self.category]


class ArxivUris:
    """ Namespaces and URIs for arXiv. Note that we are trying to use valid arxiv URLs where possible. """
    meta_graph = SB.NS['graph/arxiv-meta']

    topic_system = Uri('https://arxiv.org/category_taxonomy/')
    dataset = Uri('https://arxiv.org/')
    centi_arxiv = Uri('http://sigmathling.kwarc.info/centi-arxiv')

    arxiv_id = NameSpace('https://arxiv.org/abs/', 'arxiv:')
    arxiv_cat = NameSpace('https://arxiv.org/archive/', 'arxivcat:')