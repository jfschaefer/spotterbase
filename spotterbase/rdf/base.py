"""
A small library for RDF triples.
"""
from __future__ import annotations

import datetime
from typing import Callable, Any
from typing import Optional, Iterable

from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import XSD, RDF


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


LIT2PY_FUN: dict[Uri, Callable[[str], Any]] = {
    XSD.string: lambda s: s,
    XSD.integer: int,
    XSD.decimal: float,
    XSD.double: float,
    XSD.boolean: lambda s: {'false': False, 'true': True, '0': False, '1': True}[s],
}

PY2LIT_LIST: list[tuple[type, Callable[[Any], Literal]]] = [
    (str, lambda s: Literal(s, XSD.string)),
    (int, lambda i: Literal(str(i), XSD.integer)),
    (float, lambda f: Literal(f'{f:E}', XSD.double)),
    (bool, lambda b: Literal(str(b).lower(), XSD.boolean)),
    (datetime.datetime, lambda d: Literal(d.isoformat(), XSD.dateTime)),
]

PY2LIT_DT: dict[Uri, tuple[list[type], Callable[[Any], str]]] = {
    XSD.string: ([str], lambda s: s),
    XSD.integer: ([int], lambda i: str(i)),
    XSD.double: ([float, int], lambda f: f'{f:E}'),
    XSD.float: ([float, int], lambda f: f'{f:E}'),
    XSD.boolean: ([bool], lambda b: str(b).lower()),
    XSD.dateTime: ([datetime.datetime], lambda d: d.isoformat()),
}


class Literal:
    def __init__(self, string: str, datatype: Uri, lang_tag: Optional[str] = None):
        self.string = string
        self.datatype = datatype
        self.lang_tag = lang_tag

    def _prepare_string(self) -> str:
        return '"' + self.string.replace('\\', '\\\\') \
            .replace('"', '\\"') \
            .replace('\n', '\\n') \
            .replace('\r', '\\r') + '"'

    def to_ntriples(self) -> str:
        if self.lang_tag is not None:
            return f'{self._prepare_string()}@{self.lang_tag}'
        elif self.datatype == XSD.string:
            return self._prepare_string()
        else:
            return f'{self._prepare_string()}^^{self.datatype:<>}'

    def to_turtle(self) -> str:
        if self.datatype in {XSD.integer, XSD.decimal, XSD.double, XSD.boolean}:
            return self.string
        else:
            return self.to_ntriples()

    def get_py_val(self):
        if self.datatype not in LIT2PY_FUN:
            raise NotImplementedError(f'{self.datatype} data type not supported')
        return LIT2PY_FUN[self.datatype](self.string)

    @classmethod
    def from_py_val(cls, py_val, datatype=None) -> Literal:
        if datatype is None:
            for type_, lit_fun in PY2LIT_LIST:
                if isinstance(py_val, type_):
                    return lit_fun(py_val)
            raise TypeError(f'{type(py_val)} doesn\'t have a matching XSD type')

        if datatype not in PY2LIT_DT:
            raise ValueError(f'Unsupported datatype {datatype}')

        types, py_val_to_str = PY2LIT_DT[datatype]
        if any([isinstance(py_val, x) for x in types]):
            return cls(py_val_to_str(py_val), datatype)
        raise TypeError(f'Type {type(py_val)} is not one of the expected types {types}')

    @classmethod
    def lang_tagged(cls, string: str, lang_tag: str) -> Literal:
        return cls(string, RDF.langString, lang_tag)

    def __str__(self) -> str:
        return self.to_ntriples()

    def __repr__(self) -> str:
        return str(self)


Subject = Uri | BlankNode
Predicate = Uri
Object = Uri | BlankNode | Literal

Triple = tuple[Subject, Predicate, Object]
TripleI = Iterable[Triple]
