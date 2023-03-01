import unittest

import rdflib

from spotterbase.concept_graphs.concept_graph import PredInfo, AttrInfo, Concept, ConceptInfo
from spotterbase.concept_graphs.concept_resolver import ConceptResolver
from spotterbase.concept_graphs.jsonld_support import JsonLdConceptConverter
from spotterbase.concept_graphs.oa_support import OA_JSONLD_CONTEXT
from spotterbase.concept_graphs.sparql_populate import Populator
from spotterbase.rdf.serializer import triples_to_nt_string
from spotterbase.rdf.uri import Vocabulary, NameSpace, Uri
from spotterbase.rdf.vocab import OA
from spotterbase.sparql.endpoint import RdflibEndpoint


class TestVocab(Vocabulary):
    NS = NameSpace(Uri('http://example.org/sb-test#'), prefix='sbtest:')

    edge: Uri
    thingA: Uri
    thingB: Uri
    typeA: Uri
    typeB: Uri


class TestPredicates:
    edge: PredInfo = PredInfo(TestVocab.edge, json_ld_term='edge-in-json-ld', json_ld_type_is_id=True)
    edge2: PredInfo = PredInfo(TestVocab.edge, json_ld_term='edge2-in-json-ld', json_ld_type_is_id=True)


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
                attrs=[AttrInfo('val', TestPredicates.edge, target_type={TestVocab.typeB})],
                is_root_concept=True,
            )

            val: MiniSubConcept

        concept = MiniConcept()
        concept.val = MiniSubConcept()
        concept.val.thing = OA.Annotation
        concept.uri = TestVocab.thingA

        concept_resolver = ConceptResolver([MiniConcept, MiniSubConcept])

        # test json-ld conversion
        converter = JsonLdConceptConverter(contexts=[OA_JSONLD_CONTEXT], concept_resolver=concept_resolver)
        json_ld = converter.concept_to_json_ld(concept)
        self.assertEqual(json_ld, {'type': 'http://example.org/sb-test#typeA',
                                   'id': 'http://example.org/sb-test#thingA', 'edge-in-json-ld':
                                       {'type': 'http://example.org/sb-test#typeB', 'edge2-in-json-ld': 'Annotation'}
                                   })
        concept_2 = converter.json_ld_to_concept(json_ld)
        self.assertEqual(json_ld, converter.concept_to_json_ld(concept_2))

        # test rdf serialization/querying
        graph = rdflib.Graph()
        graph.parse(data=triples_to_nt_string(concept.to_triples()), format='nt')
        endpoint = RdflibEndpoint(graph)
        populator = Populator(concept_resolver=concept_resolver, endpoint=endpoint)
        concepts = list(populator.get_concepts(iter((concept.uri,))))
        self.assertEqual(len(concepts), 1)
        new_concept = concepts[0]
        self.assertIsInstance(new_concept, MiniConcept)
        assert isinstance(new_concept, MiniConcept)   # make mypy happy too
        self.assertEqual(new_concept.uri, concept.uri)
        self.assertEqual(new_concept.val.thing, OA.Annotation)
