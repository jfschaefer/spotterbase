from __future__ import annotations

from typing import Literal, Optional

from lxml.etree import _Element, _ElementUnicodeResult


class XmlNode:
    """ the lxml implementation of text nodes is not very convenient, so we will have wrapper for the needed nodes. """

    node: _Element
    text: bool = False
    tail: bool = False

    def __init__(self, node: _Element, text_node: Literal['text', 'tail', 'none'] = 'none'):
        self.node = node
        match text_node:
            case 'text':
                self.text = True
            case 'tail':
                self.tail = True
            case other:
                assert other == 'none'

    @classmethod
    def new(cls, node: _Element | _ElementUnicodeResult) -> XmlNode:
        match node:
            case _Element():
                return XmlNode(node)
            case _ElementUnicodeResult():
                if node.is_tail:
                    assert (parent := node.getparent()) is not None
                    return XmlNode(parent, text_node='tail')
                else:
                    assert node.is_text
                    assert (parent := node.getparent()) is not None
                    return XmlNode(parent, text_node='text')
            case _:
                raise NotImplementedError()

    def getparent(self) -> Optional[XmlNode]:
        parent = self.node.getparent()
        if parent:
            return XmlNode(parent)
        return None

    def __eq__(self, other):
        if not isinstance(other, XmlNode):
            raise NotImplementedError(f'Comparison with {type(other)} is not supported')
        return self.node == other.node and self.text == other.text and self.tail == other.tail

    def __hash__(self):
        return hash((self.node, self.text, self.tail))


def get_node_classes(node: _Element) -> list[str]:
    classes_of_node = node.get('class')
    if classes_of_node is None:
        return []
    else:
        return classes_of_node.split()
