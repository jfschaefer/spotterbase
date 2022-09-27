from typing import Optional, Iterable

from lxml.etree import _Element, _ElementUnicodeResult

from spotterbase.dnm.dnm import DomPoint
from spotterbase.dnm.token_dnm import Token, TokenGenerator
from spotterbase.dnm.xml_util import XmlNode, get_node_classes


class TextToken(Token):
    def __init__(self, node: _Element):
        assert node.text
        self.string = node.text
        self.node = XmlNode(node, text_node='text')
        assert self.string is not None

    def to_point(self, offset: int) -> DomPoint:
        return DomPoint(self.node.node, text_offset=offset)


class NodeToken(Token):
    def __init__(self, node: _Element, string: str):
        self.string = string
        self.node = XmlNode(node)

    def to_point(self, offset: int) -> DomPoint:
        assert isinstance(self.node.node, _Element)
        return DomPoint(self.node.node)


class TailToken(Token):
    def __init__(self, node: _Element):
        assert node.tail
        self.string = node.tail
        self.node = XmlNode(node, text_node='tail')
        assert self.string is not None

    def to_point(self, offset: int) -> DomPoint:
        return DomPoint(self.node.node, tail_offset=offset)


class SimpleTokenGenerator(TokenGenerator):
    """ A simple token generator that iterates through the DOM and replaces certain nodes with fixed strings """
    def __init__(self, nodes_to_replace: Optional[dict[str, str]] = None,
                 classes_to_replace: Optional[dict[str, str]] = None):
        self.nodes_to_replace = nodes_to_replace or {}
        self.classes_to_replace = classes_to_replace or {}

    def get_replacement(self, node: _Element) -> Optional[str]:
        if node.tag in self.nodes_to_replace:
            return self.nodes_to_replace[node.tag]
        for c in get_node_classes(node):
            if c in self.classes_to_replace:
                return self.classes_to_replace[c]
        return None

    def process(self, node: _Element) -> Iterable[Token]:
        replacement = self.get_replacement(node)
        if replacement is not None:
            if replacement != '':       # empty replacement -> skip node
                yield NodeToken(node, replacement)
            return

        # no replacement -> recurse
        if node.text:
            yield TextToken(node)
        for child in node:
            yield from self.process(child)
            if child.tail:
                yield TailToken(child)
