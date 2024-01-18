import functools
import hashlib
import re

from spotterbase.model_core.sb import SB
from spotterbase.rdf.uri import NameSpace, Uri


class InvalidArxivId(Exception):
    pass


class ArxivId:
    __slots__ = ('identifier',)
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

    def __str__(self) -> str:
        return self.identifier

    def __format__(self, format_spec: str) -> str:
        if format_spec == '':
            return self.identifier
        elif format_spec == 'fn':   # filename compatible
            return self.identifier.replace('/', '')
        else:
            raise ValueError(f'Unsupported format spec {format_spec!r}')

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.identifier})'

    def as_uri(self) -> Uri:
        return ArxivUris.arxiv_id[self.identifier]

    @functools.lru_cache(maxsize=2**10)
    def sha256_as_int(self) -> int:
        return int(hashlib.sha256(self.identifier.encode('utf-8')).hexdigest(), base=16)

    def is_in_deci_arxiv(self) -> bool:
        return self.sha256_as_int() % 10 == 0

    def is_in_centi_arxiv(self) -> bool:
        return self.sha256_as_int() % 100 == 0

    def is_in_milli_arxiv(self) -> bool:
        return self.sha256_as_int() % 1000 == 0

    def is_in_decimilli_arxiv(self) -> bool:
        return self.sha256_as_int() % 10000 == 0

    @property
    def yymm(self) -> str:
        if match := self.arxiv_id_regex.match(self.identifier):
            return match.group('yymm')
        raise InvalidArxivId(self.identifier)


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

    arxiv_id = NameSpace('https://arxiv.org/abs/', 'arxiv:')
    arxiv_cat = NameSpace('https://arxiv.org/archive/', 'arxivcat:')
