import io
import unittest

from lxml import etree

from spotterbase.annotations.dom_range import DomRange
from spotterbase.annotations.offset_converter import OffsetConverter
from spotterbase.annotations.selector import PathSelector, OffsetSelector
from spotterbase.annotations.selector_converter import SelectorConverter
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import SimpleTokenGenerator
from spotterbase.rdf.uri import Uri
from spotterbase.test.mixins import GraphTestMixin

# Example Dnm's:
DNM_1: TokenBasedDnm = TokenBasedDnm.from_token_generator(
    etree.parse(io.StringIO('<a>t1<b class="standard">t2</b>t3<c/>t4<d class="skip">D</d>t5</a>')),
    SimpleTokenGenerator(nodes_to_replace={'c': 'C'}, classes_to_replace={'skip': ''}))

DNM_2: TokenBasedDnm = TokenBasedDnm.from_token_generator(
    etree.parse(io.StringIO('<p>abcdef</p>')),
    SimpleTokenGenerator())

DNM_3: TokenBasedDnm = TokenBasedDnm.from_token_generator(
    etree.parse(io.StringIO('<a>AB<x>CD</x>E<y>FG</y>H</a>')),
    SimpleTokenGenerator(nodes_to_replace={'x': '', 'y': 'YZ'})
)


class TestDnm(GraphTestMixin, unittest.TestCase):
    def test_basic_string(self):
        dnmstr = DNM_1.get_dnm_str()
        self.assertEqual(dnmstr, 't1t2t3Ct4t5')
        self.assertEqual(dnmstr[5], '3')

    def test_path_selector(self):
        for dnm, index, substring, selector in [
            (DNM_1, slice(6, 8), 'Ct', PathSelector('node(/a/c)', 'char(/a,7)')),
            (DNM_1, slice(0, 1), 't', PathSelector('char(/a,0)', 'char(/a,1)')),
            (DNM_2, slice(1, 2), 'b', PathSelector('char(/p,1)', 'char(/p,2)'))
        ]:
            dnmstr = dnm.get_dnm_str()
            self.assertEqual(dnmstr[index], substring)
            dom_range: DomRange = dnmstr[index].as_range().to_dom()
            conv = SelectorConverter(Uri('http://example.org'), dom_range.start.node.getroottree().getroot())
            new_selector = conv.dom_to_path_selector(dom_range)
            self.assertEqual((new_selector.start, new_selector.end), (selector.start, selector.end))

    def test_dom_range_to_dnm_range(self):
        for dnm, selector, expected_from, expected_to, expected_str in [
            (DNM_3, OffsetSelector(start=1, end=3), 0, 1, 'AB'),
            (DNM_3, OffsetSelector(start=4, end=5), 2, 1, ''),
            (DNM_3, OffsetSelector(start=4, end=7), 2, 2, 'E'),
            (DNM_3, OffsetSelector(start=8, end=9), 3, 4, 'YZ'),
            (DNM_3, OffsetSelector(start=7, end=9), 3, 4, 'YZ'),
        ]:
            with self.subTest(selector=selector, expected_str=expected_str):
                dnm.offset_converter = OffsetConverter(dnm.tree.getroot())
                converter = SelectorConverter(Uri('http://example.org'), dnm.tree.getroot())
                dom_range = converter.selector_to_dom(selector)[0]
                assert isinstance(dom_range, DomRange)
                dnm_range, _ = dnm.dom_range_to_dnm_range(dom_range)
                self.assertEqual(dnm_range.from_.offset, expected_from)
                self.assertEqual(dnm_range.to.offset, expected_to)
                self.assertEqual(dnm.get_dnm_str(dnm_range).string, expected_str)
