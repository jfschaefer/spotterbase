from typing import Optional, Iterable

from lxml.etree import _Element

from spotterbase.dnm.dnm import DomPoint, DomRange
from spotterbase.dnm.token_dnm import Token, TokenGenerator
from spotterbase.dnm.xml_util import XmlNode, get_node_classes


class TextToken(Token):
    def __init__(self, node: _Element):
        assert node.text
        self.string = node.text
        self.node = XmlNode(node, text_node='text')
        assert self.string is not None

    def to_range(self, offset: int) -> DomRange:
        return DomPoint(self.node.node, text_offset=offset).as_range()


class NodeToken(Token):
    def __init__(self, node: _Element, string: str):
        self.string = string
        self.node = XmlNode(node)

    def to_range(self, offset: int) -> DomRange:
        assert isinstance(self.node.node, _Element)
        return DomPoint(self.node.node).as_range()


class TailToken(Token):
    def __init__(self, node: _Element):
        assert node.tail
        self.string = node.tail
        self.node = XmlNode(node, text_node='tail')
        assert self.string is not None

    def to_range(self, offset: int) -> DomRange:
        return DomPoint(self.node.node, tail_offset=offset).as_range()


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


class DefaultGenerators:
    ARXMLIV_TEXT_ONLY = SimpleTokenGenerator(
        nodes_to_replace={'head': '', 'figure': '', 'math': 'MathNode'},
        classes_to_replace={
            # to ignore
            'ltx_bibliography': '', 'ltx_page_footer': '', 'ltx_dates': '', 'ltx_authors': '',
            'ltx_role_affiliationtext': '', 'ltx_tag_equation': '', 'ltx_classification': '',
            'ltx_tag_section': '', 'ltx_tag_subsection': '',
            # to replace
            'ltx_equationgroup': 'MathGroup', 'ltx_cite': 'LtxCite',
            'ltx_ref': 'LtxRef', 'ltx_ref_tag': 'LtxRef', 'ltx_equation': 'MathEquation',
        }
    )
