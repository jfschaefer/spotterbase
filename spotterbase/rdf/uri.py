from __future__ import annotations

import functools
import pathlib
import re
import uuid
from typing import Optional

from rdflib import URIRef


class NameSpace:
    def __init__(self, uri: Uri | str, prefix: Optional[str] = None):
        if prefix and not re.match(r'([A-Za-z0-9:_]([A-Za-z0-9:_.-]*[A-Za-z0-9:_])?)?:', prefix):
            raise Exception(f'Invalid prefix: {prefix!r}')  # note: the regex does not cover all legal cases
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

    def __repr__(self):
        return f'{self.__class__.__name__}({self.uri}, prefix={self.prefix})'


class VocabularyMeta(type):
    @functools.cache
    def __getattr__(cls, item: str) -> Uri:
        if item not in cls.__annotations__:
            raise AttributeError(f'{cls.__name__} has no attribute {item}')
        assert isinstance(cls.NS, NameSpace)
        return cls.NS[item]


class Vocabulary(metaclass=VocabularyMeta):
    NS: NameSpace


class Uri:
    _suffix: str
    namespace: Optional[NameSpace]
    _full_uri: Optional[str] = None

    def __init__(self, uri: str | URIRef | pathlib.Path, namespace: Optional[NameSpace] = None):
        self.namespace = namespace
        match uri:
            case str():
                if uri.startswith('<') and uri.endswith('>'):
                    self._suffix = uri[1:-1]
                else:
                    self._suffix = uri
            case URIRef():
                self._suffix = str(uri)
            case pathlib.Path():
                self._suffix = uri.as_uri()
            case _:
                raise NotImplementedError(f'Unsupported type {type(uri)}')
        if namespace:
            assert self.full_uri().startswith(namespace.uri.full_uri())

    @classmethod
    def uuid(cls) -> Uri:
        return Uri(uuid.uuid4().urn)

    def with_namespace_from(self, namespaces: list[NameSpace]) -> Optional[Uri]:
        for namespace in sorted(namespaces, key=lambda ns: len(ns.uri.full_uri()), reverse=True):
            if self.full_uri().startswith(namespace.uri.full_uri()):
                return Uri(self.relative_to(namespace), namespace)
        return None

    def relative_to(self, other: NameSpace | str | Uri) -> str:
        other_as_str: str
        match other:
            case str():
                other_as_str = Uri(other).full_uri()
            case Uri():
                other_as_str = other.full_uri()
            case NameSpace():
                other_as_str = other.uri.full_uri()
            case _:
                raise NotImplementedError(f'Unsupported type of other: {type(other)}')
        if not self.full_uri().startswith(other_as_str):
            raise Exception(f'{self.full_uri()} does not start with {other_as_str}')
        return self.full_uri()[len(other_as_str):]

    def starts_with(self, prefix: str | Uri | NameSpace) -> bool:
        match prefix:
            case str():
                return self.full_uri().startswith(prefix)
            case Uri():
                return self.full_uri().startswith(prefix.full_uri())
            case NameSpace():
                return self.full_uri().startswith(prefix.uri.full_uri())
            case _:
                raise TypeError(f'Unsupported type {type(prefix)}')

    def __truediv__(self, other) -> Uri:
        if self._suffix.endswith('/'):
            return Uri(self._suffix + other, self.namespace)
        else:
            return Uri(self._suffix + '/' + other, self.namespace)

    def __add__(self, other) -> Uri:
        return Uri(self._suffix + other, self.namespace)

    def to_rdflib(self) -> URIRef:
        return URIRef(self._suffix)

    def __str__(self) -> str:
        return self.full_uri()

    # Note: caching might make sense, but it is not straight-forward.
    # We have Uri('http://example.org/abc') == Uri('abc', namespace=...).
    # Formatting the former with prefix will give us <http://example.org/abc>,
    # and caching that would give us the same result for the latter, which is of course undesired.
    def __format__(self, format_spec) -> str:
        reserved_chars = "~.-!$&'()*+,;=/?#@%_"
        match format_spec:
            case '' | 'plain':
                return self.full_uri()
            case '<>':
                return f'<{self.full_uri()}>'
            case 'nrprefix':  # prefixed only if no reserved characters
                if self.namespace and self.namespace.prefix and not \
                        re.match('.*[' + re.escape(reserved_chars) + '].*', self._suffix):
                    return self.namespace.prefix + self._suffix
                else:
                    return f'<{self.full_uri()}>'
            case ':' | 'prefix':
                if self.namespace and self.namespace.prefix:
                    uri = re.sub('([' + re.escape(reserved_chars) + '])', r'\\\1', self._suffix)
                    return self.namespace.prefix + uri
                else:
                    return f'<{self.full_uri()}>'
            case _:
                raise NotImplementedError(f'Unsupported format specification: {format_spec!r}')

    def full_uri(self) -> str:
        if not self._full_uri:
            if self.namespace:
                self._full_uri = self.namespace.uri.full_uri() + self._suffix
            else:
                self._full_uri = self._suffix
        return self._full_uri

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.full_uri()!r})'

    def __eq__(self, other) -> bool:
        return self.full_uri() == str(other)

    def __hash__(self):
        return hash(self.full_uri())
