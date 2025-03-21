from __future__ import annotations

import re
from typing import Optional, Any

from lxml.etree import _Element, XPathEvalError

from spotterbase.model_core import FragmentTarget
from spotterbase.model_core.selector import PathSelector, OffsetSelector, ListSelector
from spotterbase.rdf.uri import Uri, UriLike
from spotterbase.selectors.dom_range import DomRange, DomPoint
from spotterbase.selectors.offset_converter import OffsetConverter, OffsetType


# Warning: this regex is used in other places
PATH_SELECTOR_REGEX = re.compile(r'(?P<type>(node)|(after-node)|(char))\((?P<xpath>.*?)(, *(?P<offset>[0-9]+))?\)')


class SelectorConverter:
    def __init__(self, document_uri: Uri, dom: _Element, offset_converter: OffsetConverter):
        self._document_uri: Uri = document_uri
        self._dom: _Element = dom
        self._offset_converter: OffsetConverter = offset_converter

    @property
    def offset_converter(self) -> OffsetConverter:
        # Should we switch to lazy initialization?
        #   current answer: no, not worth it because the offset converter is required for most contexts anyway.
        #       by making it optional to pass an existing offset converter, we risk creating it twice.
        # Note on performance: parsing takes twice as long as creating the offset converter
        # """ Creating a text offset tracker is expensive (at least in the current implementation).
        #     Do it only if necessary. """
        # if self._offset_converter is None:
        #     self._offset_converter = OffsetConverter(self._dom)
        return self._offset_converter

    def target_to_dom(self, target: FragmentTarget) -> tuple[DomRange, Optional[list[DomRange]]]:
        assert target.source == self._document_uri
        assert target.selectors
        supported_selectors = [
            selector for selector in target.selectors
            if isinstance(selector, PathSelector) or isinstance(selector, OffsetSelector)
        ]
        if not supported_selectors:
            raise Exception('No supported selectors in target')
        return self.selector_to_dom(supported_selectors[0])

    def selector_to_dom(self, selector: OffsetSelector | PathSelector) -> tuple[DomRange, Optional[list[DomRange]]]:
        main_range: DomRange = self._simple_selector_to_dom(selector)
        if selector.refinement is not None:
            return main_range, self._complex_selector_to_dom(selector.refinement)
        else:
            return main_range, None

    def to_dom(self, arg: FragmentTarget | PathSelector | OffsetSelector) -> tuple[DomRange, Optional[list[DomRange]]]:
        if isinstance(arg, FragmentTarget):
            return self.target_to_dom(arg)
        elif isinstance(arg, PathSelector) or isinstance(arg, OffsetSelector):
            return self.selector_to_dom(arg)
        else:
            raise TypeError(f'Unsupported argument type {type(arg)}')

    def _simple_selector_to_dom(self, selector: OffsetSelector | PathSelector) -> DomRange:
        """ Like selector_to_dom, but ignores refinements and cannot handle non-continuous ranges """
        if isinstance(selector, PathSelector):
            return DomRange(self._path_to_dom_point(selector.start, True),
                            self._path_to_dom_point(selector.end, False))
        elif isinstance(selector, OffsetSelector):
            return DomRange(
                start=self.offset_converter.get_dom_point(selector.start, offset_type=OffsetType.NodeText),
                end=self.offset_converter.get_dom_point(selector.end, offset_type=OffsetType.NodeText),
            )
        else:
            raise Exception(f'Unsupported selector {type(selector)}')

    def _complex_selector_to_dom(self, selector: ListSelector) -> list[DomRange]:
        raise NotImplementedError()

    def _path_to_dom_point(self, path: str, is_start: bool) -> DomPoint:
        match = PATH_SELECTOR_REGEX.fullmatch(path)
        if match is None:
            raise Exception(f'Invalid path: {path!r}')
        try:
            node: Any = self._dom.xpath(match.group('xpath'))
        except XPathEvalError as e:
            raise Exception(f'Error occurred when evaluating xPath {path!r}') from e
        if isinstance(node, list):
            if len(node) != 1:
                raise Exception(f'XPath {path} does not yield unique node (yields {len(node)} nodes)')
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
        return self.offset_converter.get_dom_point(total_text_offset, OffsetType.Text, is_start)

    def dom_to_selectors(self, dom_range: DomRange, sub_ranges: Optional[list[DomRange]] = None)\
            -> list[PathSelector | OffsetSelector]:
        path_selector = self.dom_to_path_selector(dom_range)
        if sub_ranges:
            path_selector.refinement = ListSelector(
                [self.dom_to_path_selector(sub_range) for sub_range in sub_ranges]
            )
        offset_selector = self.dom_to_offset_selector(dom_range)
        return [path_selector, offset_selector]

    def dom_to_fragment_target(
            self, target_uri: UriLike, dom_range: DomRange, sub_ranges: Optional[list[DomRange]] = None
    ) -> FragmentTarget:
        return FragmentTarget(
            uri=target_uri,
            source=self._document_uri,
            selectors=self.dom_to_selectors(dom_range, sub_ranges)
        )

    def dom_to_offset_selector(self, dom_range: DomRange) -> OffsetSelector:
        dom_offset_range = self.offset_converter.convert_dom_range(dom_range)
        return OffsetSelector(start=dom_offset_range.start, end=dom_offset_range.end)

    def dom_to_path_selector(self, dom_range: DomRange) -> PathSelector:
        return PathSelector(
            start=self._dom_point_to_path(dom_range.start),
            end=self._dom_point_to_path(dom_range.end)
        )

    def _dom_point_to_path(self, dom_point: DomPoint) -> str:
        roottree = dom_point.node.getroottree()
        if dom_point.text_offset is not None:
            return f'char({roottree.getpath(dom_point.node)},{dom_point.text_offset + int(dom_point.after)})'
        elif dom_point.tail_offset is not None:
            offset = self.offset_converter.get_offset_data(dom_point.node).text_offset_after + dom_point.tail_offset
            parent = dom_point.node.getparent()
            assert parent is not None
            parent_offset = self.offset_converter.get_offset_data(parent).text_offset_before
            return f'char({roottree.getpath(parent)},{offset - parent_offset + int(dom_point.after)})'
        else:
            if dom_point.after:
                return f'after-node({roottree.getpath(dom_point.node)})'
            else:
                return f'node({roottree.getpath(dom_point.node)})'
