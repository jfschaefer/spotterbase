import json
import unittest
from pathlib import Path

import rdflib

from spotterbase.model_core.sb import SB_CONTEXT_FILE
from spotterbase.model_core.target import FragmentTarget, populate_standard_selectors
from spotterbase.rdf import to_rdflib
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.records.record_class_resolver import DefaultRecordClassResolver
from spotterbase.records.sparql_populate import Populator
from spotterbase.sparql.endpoint import RdflibEndpoint
from spotterbase.test.mixins import GraphTestMixin


class TestAnnotationSerialization(GraphTestMixin, unittest.TestCase):
    package_root = Path(__file__).parent.parent
    with open(SB_CONTEXT_FILE) as fp:
        sb_context = json.load(fp)
    converter = JsonLdRecordConverter.default()

    example_json_ld_files: list[Path] = [
        package_root.parent / 'doc' / 'source' / 'codesnippets' / 'example-annotation.jsonld',
        package_root.parent / 'doc' / 'source' / 'codesnippets' / 'example-target.jsonld',
    ]

    def test_jsonld_is_same_as_generated_triples(self):
        for path in self.example_json_ld_files:
            with self.subTest(file=path):
                with open(path) as fp:
                    jsonld = json.load(fp)
                my_graph = to_rdflib.triples_to_graph(self.converter.json_ld_to_record(jsonld).to_triples())
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
                    to_rdflib.triples_to_graph(self.converter.json_ld_to_record(jsonld).to_triples())
                )

                populator = Populator(record_type_resolver=DefaultRecordClassResolver,
                                      endpoint=endpoint,
                                      special_populators={
                                          FragmentTarget: [populate_standard_selectors]
                                      })
                uri = self.converter.json_ld_to_record(jsonld).require_uri()
                record = list(populator.get_records([uri]))[0]
                new_json_ld = self.converter.record_to_json_ld(record)
                self.assertEqual(jsonld, new_json_ld)
