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
    def test_stored_offsets(self):
        tree = etree.parse(io.StringIO('<p>x<emph><b>y</b></emph>za</p>'))
        conv = OffsetConverter(tree.getroot())
        p_offs = conv.get_offset_data(get_xpath_node(tree, '/p[1]'))
        emph_offs = conv.get_offset_data(get_xpath_node(tree, '/p/emph[1]'))
        b_offs = conv.get_offset_data(get_xpath_node(tree, '/p/emph/b[1]'))

        self.assertEqual(p_offs.text_offset_before, 0)
        self.assertEqual(p_offs.node_text_offset_before, 0)
        self.assertEqual(p_offs.text_offset_after, 4)
        self.assertEqual(p_offs.node_text_offset_after, 10)

        self.assertEqual(emph_offs.text_offset_before, 1)
        self.assertEqual(emph_offs.node_text_offset_before, 2)
        self.assertEqual(emph_offs.text_offset_after, 2)
        self.assertEqual(emph_offs.node_text_offset_after, 7)

        self.assertEqual(b_offs.text_offset_before, 1)
        self.assertEqual(b_offs.node_text_offset_before, 3)
        self.assertEqual(b_offs.text_offset_after, 2)
        self.assertEqual(b_offs.node_text_offset_after, 6)

    def test_basic(self):
        tree = etree.parse(io.StringIO('<p>x<emph><b>y</b></emph>za</p>'))
        conv = OffsetConverter(tree.getroot())
        node_p = get_xpath_node(tree, '/p[1]')
        node_emph = get_xpath_node(tree, '/p/emph[1]')
        node_b = get_xpath_node(tree, '/p/emph/b[1]')

        for dom_point, node_offset, test_inverse in [
            (DomPoint(node_p), 0, True),
            (DomPoint(node_p, text_offset=0), 1, True),
            (DomPoint(node_emph), 2, True),
            (DomPoint(node_p, text_offset=1), 2, False),
            (DomPoint(node_b), 3, True),
            (DomPoint(node_b, text_offset=0), 4, True),
            (DomPoint(node_b, text_offset=1), 5, True),
            (DomPoint(node_b, after=True), 6, True),
            (DomPoint(node_emph, after=True), 7, True),
            (DomPoint(node_emph, tail_offset=0), 7, False),
            (DomPoint(node_emph, tail_offset=1), 8, True),
            (DomPoint(node_emph, tail_offset=2), 9, True),
            (DomPoint(node_p, after=True), 10, True),
        ]:
            with self.subTest(dom_point=dom_point, node_offset=node_offset):
                self.assertEqual(conv.get_offset(dom_point, OffsetType.NodeText), node_offset)
                if test_inverse:
                    self.assertEqual(conv.get_dom_point(node_offset, OffsetType.NodeText), dom_point)
