from __future__ import annotations

import re
from typing import Optional, Iterable

from spotterbase.rdf.uri import UriLike, Uri, NameSpace
import spotterbase.rdf.vocab as vocab


class NameSpaceCollection:
    def __init__(self, namespaces: Optional[list[NameSpace]] = None):
        self._namespaces: list[NameSpace] = []
        self._prefixes: set[str] = set()
        self._namespace_lookup: dict[str, NameSpace] = {}
        self._trie: dict = {}
        self._regex: Optional[re.Pattern[str]] = None

        for namesepace in namespaces or []:
            self.add_namespace(namesepace)

    @classmethod
    def from_turtle(cls, turtle: str) -> NameSpaceCollection:
        """ This extracts name spaces from the @prefix directives in a turtle string.

        Note: It only supports a "reasonable" subset of turtle."""
        namespaces = []
        for line in turtle.splitlines():
            line = line.strip()
            if line.startswith('@prefix'):
                prefix, _, uri = line[len('@prefix'):].partition(':')
                namespaces.append(NameSpace(uri.strip(' .'), prefix.strip() + ':'))
        return cls(namespaces)

    def add_namespace(self, namespace: NameSpace):
        self._namespaces.append(namespace)
        # Prefixes (in particular, check for duplicates)
        if namespace.prefix:
            if namespace.prefix in self._prefixes:
                raise ValueError(f'Prefix {namespace.prefix} is already assigned to another namespace')
            self._prefixes.add(namespace.prefix)

        if str(namespace.uri) in self._namespace_lookup:
            raise ValueError(f'Already have a namespace with this URI: {namespace.uri}')
        self._namespace_lookup[str(namespace.uri)] = namespace

        # Trie
        uri_str = str(namespace.uri)
        cur = self._trie
        for c in uri_str:
            if c not in cur:
                cur[c] = {}
            cur = cur[c]
        assert '' not in cur, f'Two namespaces with the same URI: {namespace.uri}'
        cur[''] = namespace

        # invalidate regex
        self._regex = None

    def _build_regex(self):
        # Trie regex
        # (note: using a trie-based regex is more efficient than a simple regex union
        #   due to the way python's regex engine works)
        _parts: list[str] = []

        def _trie_to_regex(trie):
            if len(trie) == 1:
                key, val = list(trie.items())[0]
                if key:
                    _parts.append(re.escape(key))
                    _trie_to_regex(trie[key])
                else:       # leaf
                    pass
            else:
                _parts.append('(?:')
                for i, char in enumerate(c for c in trie if c != ''):
                    if i:
                        _parts.append('|')
                    if char:
                        _parts.append(re.escape(char))
                        _trie_to_regex(trie[char])
                if '' in trie:    # putting leafs last makes it greedy, i.e. we find the longest matching namespace
                    _parts.append('|')
                _parts.append(')')

        if self._trie:
            _trie_to_regex(self._trie)
            self._regex = re.compile(''.join(_parts))
        else:
            self._regex = None

    def namespacify(self, uri: UriLike) -> Uri:
        uri = Uri(uri)
        if not self._regex:
            self._build_regex()
        if self._regex is not None:    # if it is still None, there are no namespaces
            match = self._regex.match(str(uri))
            if match:
                return Uri(uri, self._namespace_lookup[match.group()])
        # no matching namespace found
        return uri

    def uri_from_prefixed_string(self, string: str, require_prefix_supported: bool = False) -> Uri:
        prefix, colon, suffix = string.partition(':')
        if not colon:
            raise ValueError(f'Invalid string: {string!r}')
        if prefix not in self._prefixes:
            if require_prefix_supported:
                raise ValueError(f'Unknown prefix: {prefix}')
            else:
                return Uri(string)
        return Uri(self._namespace_lookup[prefix].uri + suffix)

    def __iter__(self) -> Iterable[NameSpace]:
        return iter(self._namespaces)


EXAMPLE = NameSpace('http://example.org/', 'ex:')

StandardNameSpaces = NameSpaceCollection(
    [
        vocab.DCTERMS.NS,
        vocab.FOAF.NS,
        vocab.RDF.NS,
        vocab.RDFS.NS,
        vocab.SKOS.NS,
        EXAMPLE,
    ]
)
