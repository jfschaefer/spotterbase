from __future__ import annotations

import re
from typing import Optional

from lxml.etree import _Element

from spotterbase.annotations.dom_range import DomRange, DomPoint
from spotterbase.annotations.offset_converter import OffsetConverter, OffsetType
from spotterbase.annotations.selector import PathSelector, SimpleSelector, DiscontinuousSelector
from spotterbase.rdf.base import Uri


class SelectorConverter:
    _path_regex = re.compile(r'(?P<type>(node)|(after-node)|(char))\((?P<xpath>.*?)(, *(?P<offset>[0-9]+))?\)')

    def __init__(self, document_uri: Uri, dom: _Element):
        self._document_uri: Uri = document_uri
        self._dom: _Element = dom
        self._offset_converter: Optional[OffsetConverter] = None

    @property
    def offset_converter(self) -> OffsetConverter:
        """ Creating a text offset tracker is expensive (at least in the current implementation).
            Do it only if necessary. """
        if self._offset_converter is None:
            self._offset_converter = OffsetConverter(self._dom)
        return self._offset_converter

    def selector_to_dom(self, selector: SimpleSelector) -> tuple[DomRange, list[DomRange]]:
        main_range: DomRange = self._simple_selector_to_dom(selector)
        if selector.refinement is not None:
            return main_range, self._complex_selector_to_dom(selector.refinement)
        else:
            return main_range, [main_range]

    def _simple_selector_to_dom(self, selector: SimpleSelector) -> DomRange:
        """ Like selector_to_dom, but ignores refinements and cannot handle non-continuous ranges """
        if isinstance(selector, PathSelector):
            return DomRange(self._path_to_dom_point(selector.start),
                            self._path_to_dom_point(selector.end))
        else:
            raise Exception(f'Unsupported selector {type(selector)}')

    def _complex_selector_to_dom(self, selector: DiscontinuousSelector) -> list[DomRange]:
        ...

    def _path_to_dom_point(self, path: str) -> DomPoint:
        match = self._path_regex.fullmatch(path)
        if match is None:
            raise Exception(f'Invalid path: {path!r}')
        node = self._dom.xpath(match.group('xpath'))
        if isinstance(node, list):
            if len(node) != 1:
                raise Exception(f'XPath does not yield unique node (yields {len(node)} nodes)')
            node = node[0]
        if not isinstance(node, _Element):
            raise Exception('XPath does not point to normal node')
        type_ = match.group('type')
        offset = match.group('offset')
        if type_ in {'node', 'after-node'}:
            if offset is not None:
                raise Exception(f'No offset expected for path reference of type {type_}')
            return DomPoint(node, after=(type_ == 'after-node'))
        assert type_ == 'char'
        if offset is None:
            raise Exception(f'No offset provided for path reference of type {type_}')
        total_text_offset = int(offset) + self.offset_converter.get_offset(node, OffsetType.Text)
        return self.offset_converter.get_dom_point(total_text_offset, OffsetType.Text)
