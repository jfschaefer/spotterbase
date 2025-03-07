import io
import unittest

from lxml import etree
from spotterbase.model_core.selector import PathSelector

from spotterbase.selectors.dom_range import DomPoint, DomRange
from spotterbase.selectors.offset_converter import OffsetConverter
from spotterbase.selectors.selector_converter import SelectorConverter
from spotterbase.rdf.uri import Uri


class TestSelectorConverter(unittest.TestCase):
    def test_1(self):
        dom = etree.parse(io.StringIO('<a><b/>c</a>'))
        dom_range: DomRange = \
            DomRange(DomPoint(dom.xpath('/a/b')[0], tail_offset=0),   # type: ignore
                     DomPoint(dom.xpath('/a/b')[0], tail_offset=1))   # type: ignore
        converter = SelectorConverter(Uri('http://example.org'), dom.getroot(), OffsetConverter(dom.getroot()))
        selector = converter.dom_to_path_selector(dom_range)
        self.assertEqual(selector.start, 'char(/a,0)')

    def test2(self):
        dom = etree.parse(io.StringIO('<a><b/>xyz</a>'))
        selector = PathSelector(
            start='char(/a,1)',
            end='char(/a,2)',
        )
        converter = SelectorConverter(Uri('http://example.org'), dom.getroot(), OffsetConverter(dom.getroot()))
        dom_range, subranges = converter.selector_to_dom(selector)
        self.assertIsNone(subranges)
        selector = converter.dom_to_path_selector(dom_range)
        self.assertEqual(selector.start, 'char(/a,1)')
        self.assertEqual(selector.end, 'char(/a,2)')

    def test3(self):
        dom = etree.parse(io.StringIO('<a>u<b>vw</b>x</a>'))
        selector = PathSelector(
            start='char(/a/b,0)',
            end='char(/a/b,2)',
        )
        converter = SelectorConverter(Uri('http://example.org'), dom.getroot(), OffsetConverter(dom.getroot()))
        dom_range, subranges = converter.selector_to_dom(selector)
        self.assertIsNone(subranges)
        selector = converter.dom_to_path_selector(dom_range)
        self.assertEqual(selector.start, 'char(/a/b,0)')
        self.assertEqual(selector.end, 'char(/a/b,2)')
