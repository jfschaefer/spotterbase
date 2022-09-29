import unittest
import io

import rdflib
import rdflib.compare
from lxml import etree

from spotterbase.data.rdf import SB
from spotterbase.dnm.dnm import DomRange, Dnm
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import SimpleTokenGenerator
from spotterbase.rdf import to_rdflib
from spotterbase.rdf.vocab import RDF, OA, DCTERMS


# Example Dnm's:
DNM_1: TokenBasedDnm = TokenBasedDnm.from_token_generator(
    etree.parse(io.StringIO('<a>t1<b class="standard">t2</b>t3<c/>t4<d class="skip">D</d>t5</a>')),
    SimpleTokenGenerator(nodes_to_replace={'c': 'C'},
                         classes_to_replace={'skip': ''}))


class TestDnm(unittest.TestCase):
    def assert_equal_graphs(self, got: rdflib.Graph, expected: rdflib.Graph):
        # note: using rdflib.compare.graph_diff instead of rdflib.compare.isomorphic to support debugging
        in_both, in_first, in_second = rdflib.compare.graph_diff(got, expected)
        self.assertEqual(len(in_first), 0, f'The following triples were unexpected: {in_first.serialize()}')
        self.assertEqual(len(in_second), 0, f'The following triples missing: {in_second.serialize()}')

    def test_basic_string(self):
        dnmstr = DNM_1.get_dnm_str()
        self.assertEqual(dnmstr, 't1t2t3Ct4t5')
        self.assertEqual(dnmstr[5], '3')

    def test_point_range(self):
        for dnm, index, docfrag in [
            (DNM_1, 5, 'char(/a/text()[2],1)')
        ]:
            dnmstr = dnm.get_dnm_str()
            dom_range: DomRange = dnmstr[index].as_range().to_dom()
            point = dom_range.as_point()
            self.assertIsNotNone(point)
            self.assertEqual(point.to_docfrag_str(), docfrag)

            generated_graph = to_rdflib.Converter.convert_to_graph(dom_range.to_position()[1])
            expected_graph = rdflib.Graph().parse(data=f'''
                {RDF.NS:turtle} {OA.NS:turtle} {DCTERMS.NS:turtle} {SB.NS:turtle}
                _:sel a {OA.FragmentSelector::} ;
                    {RDF.value::} "{docfrag}" ;
                    {DCTERMS.conformsTo::} {SB.docFrag::} .
            ''')
            self.assert_equal_graphs(generated_graph, expected_graph)

    def test_nonpoint_range(self):
        for dnm, index, substring, start_docfrag, end_docfrag in [
            (DNM_1, slice(6, 8), 'Ct', 'node(/a/c)', 'char(/a/text()[3],1)')
        ]:
            dnmstr = dnm.get_dnm_str()
            self.assertEqual(dnmstr[index], substring)
            dom_range: DomRange = dnmstr[index].as_range().to_dom()

            generated_graph = to_rdflib.Converter.convert_to_graph(dom_range.to_position()[1])
            expected_graph = rdflib.Graph().parse(data=f'''
                {RDF.NS:turtle} {OA.NS:turtle} {DCTERMS.NS:turtle} {SB.NS:turtle}
                _:sel a {OA.RangeSelector::} ;
                    {OA.hasStartSelector::} [
                        a {OA.FragmentSelector::} ;
                        {RDF.value::} "{start_docfrag}" ;
                        {DCTERMS.conformsTo::} {SB.docFrag::}
                    ];
                    {OA.hasEndSelector::} [
                        a {OA.FragmentSelector::} ;
                        {RDF.value::} "{end_docfrag}" ;
                        {DCTERMS.conformsTo::} {SB.docFrag::}
                    ] .
            ''')
            self.assert_equal_graphs(generated_graph, expected_graph)
