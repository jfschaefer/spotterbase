import io
import unittest

from lxml import etree

from spotterbase.annotations.dom_range import DomRange
from spotterbase.annotations.selector import PathSelector
from spotterbase.annotations.selector_converter import SelectorConverter
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import SimpleTokenGenerator
from spotterbase.rdf.base import Uri
from spotterbase.test.mixins import GraphTestMixin

# Example Dnm's:
DNM_1: TokenBasedDnm = TokenBasedDnm.from_token_generator(
    etree.parse(io.StringIO('<a>t1<b class="standard">t2</b>t3<c/>t4<d class="skip">D</d>t5</a>')),
    SimpleTokenGenerator(nodes_to_replace={'c': 'C'},
                         classes_to_replace={'skip': ''}))


class TestDnm(GraphTestMixin, unittest.TestCase):
    def test_basic_string(self):
        dnmstr = DNM_1.get_dnm_str()
        self.assertEqual(dnmstr, 't1t2t3Ct4t5')
        self.assertEqual(dnmstr[5], '3')

    def test_nonpoint_range_selector(self):
        for dnm, index, substring, selector in [
            (DNM_1, slice(6, 8), 'Ct', PathSelector('node(/a/c)', 'char(/a,7)'))
        ]:
            dnmstr = dnm.get_dnm_str()
            self.assertEqual(dnmstr[index], substring)
            dom_range: DomRange = dnmstr[index].as_range().to_dom()
            conv = SelectorConverter(Uri('http://example.org'), dom_range.from_.node.getroottree().getroot())
            selector_range = conv.selector_to_dom(selector)[0]
            self.assertEqual(dom_range, selector_range)
