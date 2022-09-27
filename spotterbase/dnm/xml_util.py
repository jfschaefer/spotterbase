from __future__ import annotations

from lxml.etree import _Element, _ElementUnicodeResult


class XmlNode:
    """ the lxml implementation of text nodes is not very convenient, so we will have wrapper for the needed nodes. """

    node: _Element | _ElementUnicodeResult

    def __init__(self, node: _Element | _ElementUnicodeResult | XmlNode):
        if isinstance(node, XmlNode):
            self.node = node.node
        else:
            self.node = node

    def getparent(self) -> _Element:
        match self.node:
            case _Element():
                return self.node.getparent()
            case _ElementUnicodeResult():
                if self.node.is_text:
                    return self.node.getparent()
                else:
                    assert self.node.is_tail
                    # tail.getparent returns node that the tail is attached to
                    return self.node.getparent().getparent()

    def __eq__(self, other):
        if not isinstance(other, XmlNode):
            raise NotImplementedError(f'Comparison with {type(other)} is not supported')
        if isinstance(self.node, _Element):
            return self.node == other.node
        else:
            # lxml text nodes are only compared by string value
            return self.node == other.node and self.node.getparent() == other.node.getparent()

    def __hash__(self):
        if isinstance(self.node, _Element):
            return hash(self.node)
        else:
            # lxml text nodes are hashed by string value
            return hash((self.node, self.node.getparent()))


def get_node_classes(node: _Element) -> list[str]:
    classes_of_node = node.get('class')
    if classes_of_node is None:
        return []
    else:
        return classes_of_node.split()
