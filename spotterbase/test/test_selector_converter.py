import io
import unittest

from lxml import etree

from spotterbase.selectors.dom_range import DomPoint
from spotterbase.selectors.offset_converter import OffsetConverter
from spotterbase.selectors.selector_converter import SelectorConverter
from spotterbase.rdf.uri import Uri


class TestSelectorConverter(unittest.TestCase):
    def test_1(self):
        dom = etree.parse(io.StringIO('<a><b/>c</a>'))
        dom_range = DomPoint(dom.xpath('/a/b')[0], tail_offset=0).as_range()  # type: ignore
        converter = SelectorConverter(Uri('http://example.org'), dom.getroot(), OffsetConverter(dom.getroot()))
        selector = converter.dom_to_path_selector(dom_range)
        self.assertEqual(selector.start, 'char(/a,0)')
