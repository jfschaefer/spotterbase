import json
import unittest
from pathlib import Path

import rdflib

from spotterbase.annotations.concepts import ANNOTATION_CONCEPT_RESOLVER
from spotterbase.annotations.target import FragmentTarget, populate_standard_selectors
from spotterbase.concept_graphs.jsonld_support import JsonLdConceptConverter
from spotterbase.concept_graphs.oa_support import OA_JSONLD_CONTEXT
from spotterbase.concept_graphs.sb_support import SB_JSONLD_CONTEXT
from spotterbase.concept_graphs.sparql_populate import Populator
from spotterbase.rdf import to_rdflib
from spotterbase.sparql.endpoint import RdflibEndpoint
from spotterbase.test.mixins import GraphTestMixin


class TestAnnotationSerialization(GraphTestMixin, unittest.TestCase):
    package_root = Path(__file__).parent.parent
    with open(package_root / 'resources' / 'sb-context.jsonld') as fp:
        sb_context = json.load(fp)
    converter = JsonLdConceptConverter(
        contexts=[OA_JSONLD_CONTEXT, SB_JSONLD_CONTEXT],
        concept_resolver=ANNOTATION_CONCEPT_RESOLVER,
    )
    example_json_ld_files: list[Path] = [
        package_root.parent / 'doc' / 'source' / 'codesnippets' / 'example-annotation.jsonld',
        package_root.parent / 'doc' / 'source' / 'codesnippets' / 'example-target.jsonld',
    ]

    def test_jsonld_is_same_as_generated_triples(self):
        for path in self.example_json_ld_files:
            with self.subTest(file=path):
                with open(path) as fp:
                    jsonld = json.load(fp)
                my_graph = to_rdflib.triples_to_graph(self.converter.json_ld_to_concept(jsonld).to_triples())
                jsonld['@context'] = ['http://www.w3.org/ns/anno.jsonld', self.sb_context]
                json_ld_graph = rdflib.Graph().parse(data=json.dumps(jsonld), format='json-ld')

                self.assert_equal_graphs(
                    my_graph,
                    json_ld_graph,
                )

    def test_load_from_triples(self):
        for path in self.example_json_ld_files:
            with self.subTest(file=path):
                with open(path) as fp:
                    jsonld = json.load(fp)

                endpoint = RdflibEndpoint(
                    to_rdflib.triples_to_graph(self.converter.json_ld_to_concept(jsonld).to_triples())
                )

                populator = Populator(concept_resolver=ANNOTATION_CONCEPT_RESOLVER,
                                      endpoint=endpoint,
                                      special_populators={
                                          FragmentTarget: [populate_standard_selectors]
                                      })
                uri = self.converter.json_ld_to_concept(jsonld).uri
                concept = list(populator.get_concepts([uri]))[0]
                new_json_ld = self.converter.concept_to_json_ld(concept)
                self.assertEqual(jsonld, new_json_ld)
