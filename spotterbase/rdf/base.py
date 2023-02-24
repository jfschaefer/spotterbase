"""
A small library for RDF triples.
"""
from __future__ import annotations

from typing import Optional, Iterable

from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import XSD


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

    def _prepare_string(self) -> str:
        return '"' + self.string.replace('\\', '\\\\')\
                                .replace('"', '\\"')\
                                .replace('\n', '\\n')\
                                .replace('\r', '\\r') + '"'

    def to_ntriples(self):
        if self.lang_tag is not None:
            return f'{self._prepare_string()}@{self.lang_tag}'
        elif self.datatype == XSD.string:
            return self._prepare_string()
        else:
            return f'{self._prepare_string()}^^{self.datatype:<>}'

    def __str__(self) -> str:
        # TODO: change to double quotation marks!
        # Does repr(self.string) always work?
        if self.lang_tag:
            return f'{self.string!r}@{self.lang_tag}'  # datatype must be rdf:langString and can be omitted
        else:
            return f'{self.string!r}^^{self.datatype::}'

    def __repr__(self) -> str:
        return str(self)


Subject = Uri | BlankNode
Predicate = Uri
Object = Uri | BlankNode | Literal

Triple = tuple[Subject, Predicate, Object]
TripleI = Iterable[Triple]
