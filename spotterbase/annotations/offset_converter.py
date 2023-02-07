from __future__ import annotations

import bisect
import dataclasses
import enum

from lxml.etree import _Element, _Comment

from spotterbase.annotations.dom_range import DomPoint


class OffsetType(enum.Enum):
    """
    We record two types of offsets:
    * Text offsets increase with every character in a text node
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
    text_offset: int
    node_text_offset: int

    text_offset_after: int
    node_text_offset_after: int

    def get_offsets_of_type(self, offset_type: OffsetType) -> tuple[int, int]:
        if offset_type == OffsetType.Text:
            return self.text_offset, self.text_offset_after
        elif offset_type == OffsetType.NodeText:
            return self.node_text_offset, self.node_text_offset_after
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
        text_counter: int = -1
        node_counter: int = 1

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

            nodes_post_order.append(node)
            node_to_offset[node] = NodeOffsetData(
                text_offset=text_counter_start,
                node_text_offset=text_counter_start + node_counter_start,
                text_offset_after=text_counter,
                node_text_offset_after=text_counter + node_counter
            )

        recurse(root)

        self.root = root
        self._node_to_offset = node_to_offset
        self._nodes_pre_order = [(node, self._node_to_offset[node]) for node in nodes_pre_order]
        self._nodes_post_order = [(node, self._node_to_offset[node]) for node in nodes_post_order]

    def get_offset_data(self, node: _Element) -> NodeOffsetData:
        if node in self._node_to_offset:
            return self._node_to_offset[node]
        if node.getroottree().getroot() != self.root:
            raise Exception(f'Node does not belong to the tree used by this tracker')
        raise Exception(f'The node could not be found (maybe you added it to the DOM after creating the tracker?)')

    def get_offset(self, point: _Element | DomPoint, offset_type: OffsetType) -> int:
        if isinstance(point, _Element):
            return self.get_offset_data(point).get_offsets_of_type(offset_type)[0]
        node_offsets = self.get_offset_data(point.node).get_offsets_of_type(offset_type)

        if point.text_offset is not None:
            offset = node_offsets[0] + point.text_offset + 1
#             if offset_type == OffsetType.NodeText:
#                 offset += 1
            if point.after:
                offset += 1
            return offset
        elif point.tail_offset is not None:
            offset = node_offsets[1] + point.tail_offset + 1
            if point.after:
                offset += 1
            return offset
        else:   # simply a node
            if point.after:
                return node_offsets[1] + 1
            else:
                return node_offsets[0]

    def get_dom_point(self, offset: int, offset_type: OffsetType) -> DomPoint:
        assert offset >= 0
        if offset > self._nodes_post_order[-1][1].get_offsets_of_type(offset_type)[1] + 1:
            raise Exception('Offset is too large for this DOM. Maybe it refers to a different document?')
        # option 1: it's a text (not a tail)
        _shift: int = 1 if offset_type == OffsetType.Text else 0
        index = bisect.bisect_right(self._nodes_pre_order, offset,
                                    key=lambda entry: entry[1].get_offsets_of_type(offset_type)[0] + _shift) - 1
        node, offset_data = self._nodes_pre_order[index]
        offsets = offset_data.get_offsets_of_type(offset_type)
        if offsets[1] >= offset and node.text:   # it's indeed a text (not a tail)
            if offset_type == OffsetType.NodeText and offset == offsets[0]:  # actually, it's the node
                return DomPoint(node)
            return DomPoint(node, text_offset=offset-offsets[0]-1)
        # option 2: it's a tail
        index = bisect.bisect_right(self._nodes_post_order, offset,
                                    key=lambda entry: entry[1].get_offsets_of_type(offset_type)[1]) - 1
        node, offset_data = self._nodes_post_order[index]
        return DomPoint(node, tail_offset=offset-offset_data.get_offsets_of_type(offset_type)[1]-1)
