from __future__ import annotations

import datetime
from typing import Callable, Any
from typing import Optional

import lxml.html.diff
import lxml.etree as etree

from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import XSD, RDF


__all__ = ['Literal']


class HtmlFragment:
    """Value corresponding to rdf:HTML.

    This is still somewhat improvised.
    One requirement is that, unlike rdflib, I want to support lxml.
    Another requirement is that I want this to be lazy.
    I don't think lxml supports document fragments very much, so as a work-around,
    we will wrap the fragment into a <div>
    (as is also done e.g. by lxml.html.diff.[parse_html/serialize_html_fragment]).
    """
    _lxml_root: Optional[etree._Element] = None
    _literal_string: Optional[str] = None

    def __init__(self, value: etree._Element | str, wrapped_in_div: Optional[bool] = None):
        if isinstance(value, str):
            self._literal_string = value
        elif isinstance(value, etree._Element):
            if wrapped_in_div is None:
                raise ValueError('wrapped_in_div must be specified if value is an Element')
            if wrapped_in_div:
                self._lxml_root = value
            else:
                self._lxml_root = etree.Element('div')
                self._lxml_root.append(value)

    def get_wrapped_lxml_element(self) -> etree._Element:
        if self._lxml_root is None:
            self._lxml_root = lxml.html.diff.parse_html_fragment(self._literal_string)
        return self._lxml_root

    def get_literal_string(self) -> str:
        if self._literal_string is None:
            self._literal_string = lxml.html.diff.serialize_html_fragment(self._lxml_root, skip_outer=True)
        return self._literal_string


_LITERAL_TO_PYTHON_FUNCTIONS: dict[Uri, Callable[[str], Any]] = {
    XSD.string: lambda s: s,
    XSD.integer: int,
    XSD.decimal: float,
    XSD.double: float,
    XSD.boolean: lambda s: {'false': False, 'true': True, '0': False, '1': True}[s],
    XSD.nonNegativeInteger: int,    # TODO: check that not negative
    XSD.dateTime: datetime.datetime.fromisoformat,
    RDF.HTML: lambda s: HtmlFragment(s),
}

_PYTHON_TO_LITERAL: list[tuple[type, Callable[[Any], Literal]]] = [
    (str, lambda s: Literal(s, XSD.string)),
    (int, lambda i: Literal(str(i), XSD.integer)),
    (float, lambda f: Literal(f'{f:E}', XSD.double)),
    (bool, lambda b: Literal(str(b).lower(), XSD.boolean)),
    (datetime.datetime, lambda d: Literal(d.isoformat(), XSD.dateTime)),
    (HtmlFragment, lambda h: Literal(h.get_literal_string(), RDF.HTML)),
]

_PYTHON_TO_LITERAL_WITH_DATATYPE: dict[Uri, tuple[list[type], Callable[[Any], str]]] = {
    XSD.string: ([str], lambda s: s),
    XSD.integer: ([int], lambda i: str(i)),
    XSD.double: ([float, int], lambda f: f'{f:E}'),
    XSD.float: ([float, int], lambda f: f'{f:E}'),
    XSD.boolean: ([bool], lambda b: str(b).lower()),
    XSD.dateTime: ([datetime.datetime], lambda d: d.isoformat()),
    XSD.nonNegativeInteger: ([int], lambda i: str(i)),
    RDF.HTML: ([HtmlFragment], lambda h: h.get_literal_string()),
}


class Literal:
    def __init__(self, string: str, datatype: Optional[Uri] = None, lang_tag: Optional[str] = None):
        self.string: str = string
        if datatype is None:
            datatype = XSD.string if lang_tag is None else RDF.langString
        self.datatype: Uri = datatype
        self.lang_tag: Optional[str] = lang_tag

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

    def to_py_val(self):
        if self.datatype not in _LITERAL_TO_PYTHON_FUNCTIONS:
            raise NotImplementedError(f'{self.datatype} data type not supported')
        return _LITERAL_TO_PYTHON_FUNCTIONS[self.datatype](self.string)

    @classmethod
    def from_py_val(cls, py_val, datatype=None) -> Literal:
        if datatype is None:
            for type_, lit_fun in _PYTHON_TO_LITERAL:
                if isinstance(py_val, type_):
                    return lit_fun(py_val)
            raise TypeError(f'{type(py_val)} doesn\'t have a matching XSD type')

        if datatype not in _PYTHON_TO_LITERAL_WITH_DATATYPE:
            raise ValueError(f'Unsupported datatype {datatype}')

        types, py_val_to_str = _PYTHON_TO_LITERAL_WITH_DATATYPE[datatype]
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

    def __format__(self, format_spec) -> str:
        if format_spec in {'turtle', 'ttl'}:
            return self.to_turtle()
        elif format_spec in {'', 'nt'}:
            return self.to_ntriples()
        else:
            raise Exception(f'Unsupported format: {format_spec!r}')
