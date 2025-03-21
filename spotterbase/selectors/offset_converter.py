from __future__ import annotations

import bisect
import dataclasses
import enum
from typing import Optional

from lxml.etree import _Element, _Comment

from spotterbase.selectors.dom_range import DomPoint, DomRange


class DomOffsetRange:
    """ A DomRange, except that it uses node offsets as created by the OffsetConverter """
    __slots__ = ('start', 'end', 'converter')
    start: int
    end: int
    converter: OffsetConverter

    def __init__(self, start: int, end: int, converter: OffsetConverter):
        self.start = start
        self.end = end
        self.converter = converter

    def to_dom_range(self) -> DomRange:
        return DomRange(
            self.converter.get_dom_point(self.start, OffsetType.NodeText),
            self.converter.get_dom_point(self.end, OffsetType.NodeText)
        )

    def __repr__(self) -> str:
        return f'DomOffsetRange({self.start}, {self.end})'


class OffsetType(enum.Enum):
    """
    We record two types of offsets:
    * Text offsets increase with every character in a text node
        (we need this for the `char` because it only counts text)
    * Node text offsets additionally increase with every opening tag
    """
    Text = 0
    NodeText = 1


@dataclasses.dataclass(slots=True)
class NodeOffsetData:
    """ Two types of offsets are recorded: text offsets and node text offsets.
    These offsets are recorded both for the node itself and for the first element after the node.

    The text offset correspond to the number of characters in text nodes until then.
    The node text offset additionally counts all nodes (opening tags).
    The node text offsets allows targeting nodes directly.
    That way, it's possible to target e.g. an <img .../> node or to distinguish
    whether the <mrow>, the <mi> or the n is targeted in <mrow><mi>n</mi>....

    Details:
    * text_offset is the offset of the last character before the node
    * node_text_offset is the offset of the node itself
    """
    text_offset_before: int
    node_text_offset_before: int

    text_offset_after: int
    node_text_offset_after: int

    def get_offsets_of_type(self, offset_type: OffsetType) -> tuple[int, int]:
        if offset_type == OffsetType.Text:
            return self.text_offset_before, self.text_offset_after
        elif offset_type == OffsetType.NodeText:
            return self.node_text_offset_before, self.node_text_offset_after
        else:
            raise Exception('Unsupported offset type')


class OffsetConverter:
    """ Records offsets in the DOM.

    Notes on efficiency:

    * Recurses through entire DOM at initialization, which takes time (approximately 1/6th of parsing time).
    * If a single offset is of interest, using an html tree (`lxml.html.parse`) and `.text_content()`
        with a custom implementation is every efficient (10x faster).
        However, I expect that there will often be more than 10 offets to convert.
    """

    root: _Element
    _node_to_offset: dict[_Element, NodeOffsetData]
    _nodes_pre_order: list[tuple[_Element, NodeOffsetData]]
    _nodes_post_order: list[tuple[_Element, NodeOffsetData]]

    def __init__(self, root: _Element):
        node_to_offset = {}
        nodes_pre_order = []
        nodes_post_order = []
        text_counter: int = 0
        node_counter: int = 0

        def recurse(node: _Element):
            nonlocal text_counter, node_counter
            text_counter_start = text_counter
            node_counter_start = node_counter
            nodes_pre_order.append(node)

            if t := node.text:
                text_counter += len(t)

            for child in node.iterchildren():
                skip = isinstance(child, _Comment)  # it's probably better to ignore comments...
                if not skip:
                    node_counter += 1
                    recurse(child)
                if t := child.tail:
                    text_counter += len(t)

            node_counter += 1

            nodes_post_order.append(node)
            node_to_offset[node] = NodeOffsetData(
                text_offset_before=text_counter_start,
                node_text_offset_before=text_counter_start + node_counter_start,
                text_offset_after=text_counter,
                node_text_offset_after=text_counter + node_counter + 1
            )

        recurse(root)

        self.root = root
        self._node_to_offset = node_to_offset
        self._nodes_pre_order = [(node, node_to_offset[node]) for node in nodes_pre_order]
        self._nodes_post_order = [(node, node_to_offset[node]) for node in nodes_post_order]

    def get_offset_data(self, node: _Element) -> NodeOffsetData:
        if node in self._node_to_offset:
            return self._node_to_offset[node]
        if node.getroottree().getroot() != self.root:
            raise Exception('Node does not belong to the tree used by this tracker')
        if not isinstance(node, _Element):
            raise ValueError(f'{node} is not a valid XML node')
        raise Exception('The node could not be found (maybe you added it to the DOM after creating the tracker?)')

    def get_offset(self, point: _Element | DomPoint, offset_type: OffsetType) -> int:
        if isinstance(point, _Element):
            return self.get_offset_data(point).get_offsets_of_type(offset_type)[0]
        if offset_type != OffsetType.NodeText:
            # this requires careful design and some testing.
            raise Exception('Getting text offsets for a DomPoint is not supported')

        node_offsets = self.get_offset_data(point.node).get_offsets_of_type(offset_type)

        if point.text_offset is not None:
            offset = node_offsets[0] + point.text_offset + 1
            if point.after:
                offset += 1
            return offset
        elif point.tail_offset is not None:
            offset = node_offsets[1] + point.tail_offset
            if point.after:
                offset += 1
            return offset
        else:   # simply a node
            if point.after:
                return node_offsets[1]
            else:
                return node_offsets[0]

    def get_dom_point(self, offset: int, offset_type: OffsetType, is_start: Optional[bool] = None) -> DomPoint:
        assert offset >= 0
        if offset > self._nodes_post_order[-1][1].get_offsets_of_type(offset_type)[1] + 1:
            raise Exception('Offset is too large for this DOM. Maybe it refers to a different document?')

        if offset_type == OffsetType.NodeText:
            return self._get_dom_point_node_text(offset)
        else:
            assert offset_type == OffsetType.Text
            assert is_start is not None

            offset_alt = offset
            if not is_start:
                offset_alt -= 1

            index = bisect.bisect_right(self._nodes_pre_order, offset_alt,
                                        key=lambda entry: entry[1].get_offsets_of_type(OffsetType.Text)[0]) - 1
            node, offset_data = self._nodes_pre_order[index]
            offsets = offset_data.get_offsets_of_type(OffsetType.Text)
            if offsets[1] > offset_alt:
                return DomPoint(node, text_offset=offset - offsets[0])
            index = bisect.bisect_right(self._nodes_post_order, offset_alt,
                                        key=lambda entry: entry[1].get_offsets_of_type(OffsetType.Text)[1]) - 1
            node, offset_data = self._nodes_post_order[index]
            offsets = offset_data.get_offsets_of_type(OffsetType.Text)
            return DomPoint(node, tail_offset=offset - offsets[1])

    def _get_dom_point_node_text(self, offset: int):
        # option 1: it's a text (not a tail)
        index = bisect.bisect_right(self._nodes_pre_order, offset,
                                    key=lambda entry: entry[1].get_offsets_of_type(OffsetType.NodeText)[0]) - 1
        node, offset_data = self._nodes_pre_order[index]
        offsets = offset_data.get_offsets_of_type(OffsetType.NodeText)
        if offsets[1] >= offset:
            if offset == offsets[0]:  # actually, it's the node
                return DomPoint(node)
            if offset == offsets[1]:
                return DomPoint(node, after=True)
            return DomPoint(node, text_offset=offset - offsets[0] - 1)
        # option 2: it's a tail
        index = bisect.bisect_right(self._nodes_post_order, offset,
                                    key=lambda entry: entry[1].get_offsets_of_type(OffsetType.NodeText)[1]) - 1
        node, offset_data = self._nodes_post_order[index]
        offsets = offset_data.get_offsets_of_type(OffsetType.NodeText)
        if offsets[1] == offset:
            return DomPoint(node, after=True)
        return DomPoint(node, tail_offset=offset - offsets[1])

    def convert_dom_range(self, dom_range: DomRange) -> DomOffsetRange:
        return DomOffsetRange(
            start=self.get_offset(dom_range.start, offset_type=OffsetType.NodeText),
            end=self.get_offset(dom_range.end, offset_type=OffsetType.NodeText),
            converter=self
        )
