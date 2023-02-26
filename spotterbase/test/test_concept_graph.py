import unittest

from spotterbase.concept_graphs.concept_graph import PredInfo, AttrInfo, Concept, ConceptInfo
from spotterbase.concept_graphs.concept_resolver import ConceptResolver
from spotterbase.concept_graphs.jsonld_support import JsonLdConceptConverter
from spotterbase.concept_graphs.oa_support import OA_JSONLD_CONTEXT
from spotterbase.rdf.uri import Vocabulary, NameSpace, Uri


class TestVocab(Vocabulary):
    NS = NameSpace(Uri('http://example.org/sb-test#'), prefix='sbtest:')

    edge: Uri
    thingA: Uri
    thingB: Uri
    typeA: Uri
    typeB: Uri


class TestPredicates:
    edge: PredInfo = PredInfo(TestVocab.edge, 'edge-in-json-ld')
    edge2: PredInfo = PredInfo(TestVocab.edge, 'edge2-in-json-ld')


class TestConceptGraph(unittest.TestCase):
    def test_simple(self):
        class MiniSubConcept(Concept):
            concept_info = ConceptInfo(
                concept_type=TestVocab.typeB,
                attrs=[AttrInfo('thing', TestPredicates.edge2)]
            )

            thing: Uri

        class MiniConcept(Concept):
            concept_info = ConceptInfo(
                concept_type=TestVocab.typeA,
                attrs=[AttrInfo('val', TestPredicates.edge)],
                is_root_concept=True,
            )

            val: MiniSubConcept

        concept = MiniConcept()
        concept.val = MiniSubConcept()
        concept.val.thing = Uri('http://www.w3.org/ns/oa#Annotation')
        concept.uri = TestVocab.thingA

        converter = JsonLdConceptConverter(contexts=[OA_JSONLD_CONTEXT],
                                           concept_resolver=ConceptResolver([MiniConcept, MiniSubConcept])
                                           )
        json_ld = converter.concept_to_json_ld(concept)
        self.assertEqual(json_ld, {'type': 'http://example.org/sb-test#typeA',
                                   'id': 'http://example.org/sb-test#thingA', 'edge-in-json-ld':
                                       {'type': 'http://example.org/sb-test#typeB', 'edge2-in-json-ld': 'Annotation'}
                                   })
        concept_2 = converter.json_ld_to_concept(json_ld)
        self.assertEqual(json_ld, converter.concept_to_json_ld(concept_2))
