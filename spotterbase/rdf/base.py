"""
A small library for RDF triples.
"""
from __future__ import annotations

import dataclasses
import functools
import pathlib
import re
from typing import Optional, Iterable

from rdflib import URIRef


class NameSpace:
    def __init__(self, uri: Uri | str, prefix: Optional[str] = None):
        self.uri = uri if isinstance(uri, Uri) else Uri(uri)
        self.prefix = prefix

    def __getitem__(self, item) -> Uri:
        assert isinstance(item, str)
        return Uri(item, self)

    def __format__(self, format_spec) -> str:
        match format_spec:
            case 'sparql':
                return f'PREFIX {self.prefix} {self.uri:<>}'
            case 'turtle' | 'ttl':
                return f'@prefix {self.prefix} {self.uri:<>} .'
            case other:
                raise Exception(f'Unsupported format: {other!r}')


class VocabularyMeta(type):
    @functools.cache
    def __getattr__(cls, item: str) -> Uri:
        if item not in cls.__annotations__:
            raise AttributeError(f'{cls.__name__} has no attribute {item}')
        return cls.NS[item]


class Vocabulary(metaclass=VocabularyMeta):
    NS: NameSpace


class Uri:
    uri: str
    namespace: Optional[NameSpace]
    _full_uri: Optional[str] = None

    def __init__(self, uri: str | URIRef | pathlib.Path, namespace: Optional[NameSpace] = None):
        self.namespace = namespace
        match uri:
            case str():
                if uri.startswith('<') and uri.endswith('>'):
                    self.uri = uri[1:-1]
                else:
                    self.uri = uri
            case URIRef():
                self.uri = str(uri)
            case pathlib.Path():
                self.uri = uri.as_uri()
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

    @functools.cache
    def __format__(self, format_spec) -> str:
        match format_spec:
            case '' | 'plain':
                return self.full_uri()
            case '<>':
                return f'<{self.full_uri()}>'
            case ':' | 'prefix':
                if self.namespace and self.namespace.prefix:
                    reserved_chars = "~.-!$&'()*+,;=/?#@%_"
                    uri = re.sub('([' + re.escape(reserved_chars) + '])', r'\\\1', self.uri)
                    return self.namespace.prefix + uri
                else:
                    return f'<{self.full_uri()}>'
            case other:
                raise NotImplementedError(f'Unsupported format specification: {format_spec!r}')

    def full_uri(self) -> str:
        if not self._full_uri:
            if self.namespace:
                self._full_uri = self.namespace.uri.full_uri() + self.uri
            else:
                self._full_uri = self.uri
        return self._full_uri

    def __repr__(self) -> str:
        return format(self, '<>')

    def __eq__(self, other) -> bool:
        return self.full_uri() == str(other)

    def __hash__(self):
        return hash(self.full_uri())

    # def __sub__(self, other) -> :


class BlankNode:
    counter: int = 0

    def __init__(self):
        # must have unique value
        self.value = hex(BlankNode.counter)[2:]
        BlankNode.counter += 1

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def __str__(self):
        return f'_:{self.value}'


class Literal:
    def __init__(self, string: str, datatype: Uri, lang_tag: Optional[str] = None):
        self.string = string
        self.datatype = datatype
        self.lang_tag = lang_tag

    def __str__(self) -> str:
        # Does repr(self.string) always work?
        if self.lang_tag:
            return f'{self.string!r}@{self.lang_tag}'   # datatype must be xsd:langString and can be omitted
        else:
            return f'{self.string!r}^^{self.datatype::}'


Subject = Uri | BlankNode
Predicate = Uri
Object = Uri | BlankNode | Literal

Triple = tuple[Subject, Predicate, Object]
TripleI = Iterable[Triple]
