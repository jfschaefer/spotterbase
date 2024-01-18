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
        self._uri = uri if isinstance(uri, Uri) else Uri(uri)
        self._prefix = prefix

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    @property
    def uri(self) -> Uri:
        return self._uri

    def __getitem__(self, item) -> Uri:
        assert isinstance(item, str)
        return Uri(self._uri + item, self)

    def __format__(self, format_spec) -> str:
        if self._prefix is None:
            raise Exception(f'Cannot format namespace {self!r} without prefix')
        match format_spec:
            case 'sparql':
                return f'PREFIX {self._prefix} {self._uri:<>}'
            case 'turtle' | 'ttl':
                return f'@prefix {self._prefix} {self._uri:<>} .'
            case other:
                raise Exception(f'Unsupported format: {other!r}')

    def __repr__(self):
        return f'{self.__class__.__name__}({self._uri}, prefix={self._prefix})'


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
    __slots__ = ('_full_uri', '_namespace')

    _namespace: Optional[NameSpace]
    _full_uri: str

    def __init__(self, uri: UriLike, namespace: Optional[NameSpace] = None):
        if isinstance(uri, str) and not isinstance(uri, URIRef):   # URIRef is a subclass of str
            if uri.startswith('<') and uri.endswith('>'):
                self._full_uri = uri[1:-1]
            else:
                self._full_uri = uri
        elif isinstance(uri, Uri):      # TODO: we could catch this in __new__ and avoid the copy
            self._full_uri = uri._full_uri
            self._namespace = uri._namespace
        elif isinstance(uri, URIRef):
            self._full_uri = str(uri)
        elif isinstance(uri, pathlib.Path):
            self._full_uri = uri.as_uri()
        elif isinstance(uri, VocabularyMeta):
            self._full_uri = str(uri.NS.uri)  # type: ignore
        else:
            raise TypeError(f'Unsupported argument type {type(uri)}')

        if namespace:
            assert self._full_uri.startswith(str(namespace.uri))
            self._namespace = namespace
        elif not hasattr(self, '_namespace'):
            self._namespace = None

    @classmethod
    def maybe(cls, uri: Optional[UriLike]) -> Optional[Uri]:
        if uri is None:
            return None
        else:
            return cls(uri)

    @property
    def namespace(self) -> Optional[NameSpace]:
        return self._namespace

    @classmethod
    def uuid(cls) -> Uri:
        return Uri(uuid.uuid4().urn)

    def relative_to(self, other: NameSpace | str | Uri) -> str:
        other_as_str: str
        match other:
            case str():
                other_as_str = str(Uri(other))
            case Uri():
                other_as_str = str(other)
            case NameSpace():
                other_as_str = str(other.uri)
            case _:
                raise TypeError(f'Unsupported type of other: {type(other)}')
        if not str(self).startswith(other_as_str):
            raise Exception(f'{str(self)} does not start with {other_as_str}')
        return str(self)[len(other_as_str):]

    def starts_with(self, prefix: str | Uri | NameSpace) -> bool:
        match prefix:
            case str():
                return str(self).startswith(prefix)
            case Uri():
                return str(self).startswith(str(prefix))
            case NameSpace():
                return str(self).startswith(str(prefix.uri))
            case _:
                raise TypeError(f'Unsupported type {type(prefix)}')

    def __truediv__(self, other) -> Uri:
        if self._full_uri.endswith('/'):
            return Uri(self._full_uri + other, self._namespace)
        else:
            return Uri(self._full_uri + '/' + other, self._namespace)

    def __add__(self, other) -> Uri:
        return Uri(self._full_uri + other, self._namespace)

    def to_rdflib(self) -> URIRef:
        return URIRef(self._full_uri)

    def __str__(self) -> str:
        return self._full_uri

    # Note: caching might make sense, but it is not straight-forward
    # (equal URIs can be associated with different namespaces/prefixes)
    def __format__(self, format_spec) -> str:
        reserved_chars = "~.-!$&'()*+,;=/?#@%_"
        match format_spec:
            case '' | 'plain':
                return str(self)
            case '<>':
                return f'<{str(self)}>'
            case 'nrprefix':  # prefixed only if no reserved characters
                if self._namespace and self._namespace.prefix:
                    suffix = str(self)[len(str(self._namespace.uri)):]
                    if not re.match('.*[' + re.escape(reserved_chars) + '].*', suffix):
                        return self._namespace.prefix + suffix
                return f'<{str(self)}>'
            case ':' | 'prefix':
                if self._namespace and self._namespace.prefix:
                    suffix = str(self)[len(str(self._namespace.uri)):]
                    uri = re.sub('([' + re.escape(reserved_chars) + '])', r'\\\1', suffix)
                    return self._namespace.prefix + uri
                else:
                    return f'<{str(self)}>'
            case _:
                raise ValueError(f'Unsupported format specification: {format_spec!r}')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str(self)!r})'

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


# Anything that can be converted to a Uri
UriLike = str | Uri | URIRef | pathlib.Path | VocabularyMeta
