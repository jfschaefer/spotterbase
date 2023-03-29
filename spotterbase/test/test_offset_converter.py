import io
import unittest

from lxml import etree
from lxml.etree import _Element, _ElementTree

from spotterbase.selectors.dom_range import DomPoint
from spotterbase.selectors.offset_converter import OffsetConverter, OffsetType


def get_xpath_node(tree: _ElementTree, xpath: str) -> _Element:
    result = tree.xpath(xpath)
    assert isinstance(result, list)
    node = result[0]
    assert isinstance(node, _Element)
    return node


class TestOffsetConverter(unittest.TestCase):
    def test_basic(self):
        tree = etree.parse(io.StringIO('<u>ab<v>cd</v>ef<w/>gh<x>ij</x>kl</u>'))
        # offsets:                       0 12 3 45    67 8  910111213 1415
        conv = OffsetConverter(tree.getroot())

        node_u = get_xpath_node(tree, '/u[1]')
        node_v = get_xpath_node(tree, '/u/v[1]')
        node_w = get_xpath_node(tree, '/u/w[1]')

        for dom_point, node_offset in [
            (DomPoint(node_u), 0),
            (DomPoint(node_u, text_offset=0), 1),
            (DomPoint(node_u, text_offset=1), 2),
            (DomPoint(node_v), 3),
            (DomPoint(node_v, text_offset=1), 5),
            (DomPoint(node_v, tail_offset=1), 7),
            (DomPoint(node_w, tail_offset=0), 9),
            # after
            (DomPoint(node_v, after=True), 6),
            (DomPoint(node_w, after=True), 9),
            (DomPoint(node_v, text_offset=0, after=True), 5),
            (DomPoint(node_v, text_offset=1, after=True), 6),
            (DomPoint(node_v, tail_offset=1, after=True), 8),
        ]:
            with self.subTest(dom_point=dom_point, node_offset=node_offset):
                self.assertEqual(conv.get_offset(dom_point, OffsetType.NodeText), node_offset)
                if not dom_point.after:
                    self.assertEqual(conv.get_dom_point(node_offset, OffsetType.NodeText), dom_point)
