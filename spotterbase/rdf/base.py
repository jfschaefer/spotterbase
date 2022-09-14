from __future__ import annotations

import dataclasses
import functools
import re
import typing
from typing import Optional, TypeVar, Type

from rdflib import URIRef


# https://www.w3.org/TR/turtle/#sec-grammar-grammar

class NameSpace:
    def __init__(self, uri: Uri, prefix: Optional[str] = None):
        self.uri = uri
        self.prefix = prefix

    def __getitem__(self, item) -> Uri:
        assert isinstance(item, str)
        return Uri(item, self)

    def format(self, format: typing.Literal['sparql', 'turtle']) -> str:
        match format:
            case 'sparql':
                return f'@prefix {self.prefix} {self.uri.format(with_angular_brackets=True)} .'
            case 'turtle':
                return f'PREFIX {self.prefix} {self.uri.format(with_angular_brackets=True)}'
            case other:
                raise Exception(f'Unsupported format: "{other}"')


class VocabularyMeta(type):
    @functools.cache
    def __getattr__(cls, item: str) -> Uri:
        if item not in cls.__annotations__:
            raise AttributeError(f'{cls.__class__} has no attribute {item}')
        class_ = cls.__annotations__[item]
        assert issubclass(class_, Uri)
        uri = cls.NS[item]
        return class_.from_uri(uri)


class Vocabulary(metaclass=VocabularyMeta):
    NS: NameSpace


_T = TypeVar('_T', bound='Uri')


class Uri:
    uri: str
    namespace: Optional[NameSpace]
    _full_uri: Optional[str] = None

    def __init__(self, uri: str, namespace: Optional[NameSpace] = None):
        self.namespace = namespace
        match uri:
            case str():
                if uri.startswith('<') and uri.endswith('>'):
                    self.uri = uri[1:-1]
                else:
                    self.uri = uri
            case URIRef():
                self.uri = str(uri)
            case _:
                raise NotImplementedError(f'Unsupported type {type(uri)}')
        if namespace:
            assert self.full_uri().startswith(namespace.uri.full_uri())

    def __truediv__(self, other) -> Uri:
        if self.uri.endswith('/'):
            return Uri(self.uri + other, self.namespace)
        else:
            return Uri(self.uri + '/' + other, self.namespace)

    def __add__(self, other) -> Uri:
        return Uri(self.uri + other, self.namespace)

    def as_uriref(self) -> URIRef:
        return URIRef(self.uri)

    def __str__(self) -> str:
        return self.full_uri()

    def format(self, with_angular_brackets: bool = False, allow_prefixed: bool = False) -> str:
        if allow_prefixed:
            if self.namespace and self.namespace.prefix:
                reserved_chars = "~.-!$&'()*+,;=/?#@%_"
                uri = re.sub('([' + re.escape(reserved_chars) + '])', r'\\\1', self.uri)
                return self.namespace.prefix + uri
        if with_angular_brackets:
            return f'<{self.full_uri()}>'
        else:
            return self.full_uri()

    def full_uri(self) -> str:
        if not self._full_uri:
            if self.namespace:
                self._full_uri = self.namespace.uri.full_uri() + self.uri
            else:
                self._full_uri = self.uri
        return self._full_uri

    def __repr__(self) -> str:
        return self.format(with_angular_brackets=True)

    @classmethod
    def from_uri(cls: Type[_T], uri: Uri) -> _T:
        return cls(uri.uri, uri.namespace)

    def __eq__(self, other) -> bool:
        return self.full_uri() == str(other)

    def __hash__(self):
        return hash(self.full_uri())


class BlankNode:
    counter: int = 0

    def __init__(self):
        # must have unique value
        self.value = hex(BlankNode.counter)[2:]
        BlankNode.counter += 1


class Literal:
    pass


Subject = Uri | BlankNode
Predicate = Uri
Object = Uri | BlankNode | Literal


@dataclasses.dataclass
class Triple:
    s: Subject
    p: Predicate
    o: Object
