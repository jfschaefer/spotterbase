import io
import unittest

from lxml import etree

from spotterbase.dnm.dnm import Dnm
from spotterbase.dnm.node_based_dnm_factory import TextExtractingNP, SkippingNP, ReplacingNP, NodeBasedDnmFactory
from spotterbase.dnm.replacement_pattern import StandardReplacementPattern, CategoryStyle
from spotterbase.dnm.simple_dnm_factory import SimpleDnmFactory
from spotterbase.model_core.selector import PathSelector, OffsetSelector
from spotterbase.selectors.dom_range import DomRange
from spotterbase.test.mixins import GraphTestMixin

# Example DNMs:
DNM_1: Dnm = SimpleDnmFactory(nodes_to_replace={'c': 'C'}, classes_to_replace={'skip': ''}).anonymous_dnm_from_node(
    etree.parse(io.StringIO('<a>t1<b class="standard">t2</b>t3<c/>t4<d class="skip">D</d>t5</a>')).getroot()
)

DNM_2: Dnm = SimpleDnmFactory().anonymous_dnm_from_node(
    etree.parse(io.StringIO('<p>abcdef</p>')).getroot()
)

DNM_3: Dnm = SimpleDnmFactory(nodes_to_replace={'x': '', 'y': 'YZ'}).anonymous_dnm_from_node(
    etree.parse(io.StringIO('<a>AB<x>CD</x>E<y>FG</y>H</a>')).getroot()
)


def _compute_dnm_3_with_nodebased_factory():
    processor = TextExtractingNP()
    processor.register_tag_processor('x', SkippingNP())
    processor.register_tag_processor('y', ReplacingNP(
        StandardReplacementPattern(category_style=CategoryStyle.ALL_CAPS),
        'yz',
        number_replacements=False,
    ))
    return NodeBasedDnmFactory(processor).anonymous_dnm_from_node(
        etree.parse(io.StringIO('<a>AB<x>CD</x>E<y>FG</y>H</a>')).getroot()
    )


DNM_3_NODEBASED: Dnm = _compute_dnm_3_with_nodebased_factory()


class TestDnm(GraphTestMixin, unittest.TestCase):
    def test_basic_string(self):
        dnm = DNM_1
        self.assertEqual(str(dnm), 't1t2t3Ct4t5')
        self.assertEqual(str(dnm[5]), '3')

    def test_path_selector(self):
        for dnm, index, substring, selector in [
            (DNM_1, slice(6, 8), 'Ct', PathSelector('node(/a/c)', 'char(/a,7)')),
            (DNM_1, slice(0, 1), 't', PathSelector('char(/a,0)', 'char(/a,1)')),
            (DNM_2, slice(1, 2), 'b', PathSelector('char(/p,1)', 'char(/p,2)'))
        ]:
            with self.subTest(substring=substring, selector=selector):
                self.assertEqual(str(dnm[index]), substring)
                dom_range: DomRange = dnm[index].to_dom()
                conv = dnm.get_meta_info().selector_converter
                new_selector = conv.dom_to_path_selector(dom_range)
                self.assertEqual((new_selector.start, new_selector.end), (selector.start, selector.end))

    def test_node_based_matches_simple(self):
        """Test that the node-based factory creates the same DNM as the simple factory"""
        self.assertEqual(str(DNM_3), str(DNM_3_NODEBASED))
        self.assertEqual((DNM_3.get_start_refs(), DNM_3.get_end_refs()),
                         (DNM_3_NODEBASED.get_start_refs(), DNM_3_NODEBASED.get_end_refs()))

    def test_dom_range_to_dnm_range(self):
        for dnm, selector, expected_from, expected_to, expected_str in [
            (DNM_3, OffsetSelector(start=1, end=3), 0, 2, 'AB'),
            (DNM_3, OffsetSelector(start=4, end=5), 2, 2, ''),
            (DNM_3, OffsetSelector(start=4, end=8), 2, 3, 'E'),
            (DNM_3, OffsetSelector(start=9, end=10), 3, 5, 'YZ'),
            (DNM_3, OffsetSelector(start=8, end=10), 3, 5, 'YZ'),
        ]:
            with self.subTest(selector=selector, expected_str=expected_str):
                converter = dnm.get_meta_info().selector_converter
                dom_range = converter.selector_to_dom(selector)[0]
                assert isinstance(dom_range, DomRange)

                sub_dnm, _ = dnm.sub_dnm_from_dom_range(dom_range)
                self.assertEqual(str(sub_dnm), expected_str)

                required_range = dnm.get_meta_info().offset_converter.convert_dom_range(dom_range)
                from_, to = dnm.get_indices_from_ref_range(required_range.start, required_range.end)
                self.assertEqual(from_, expected_from)
                self.assertEqual(to, expected_to)
