import json
import unittest
from pathlib import Path

import rdflib

from spotterbase.annotations.concepts import ANNOTATION_CONCEPT_RESOLVER
from spotterbase.concept_graphs.jsonld_support import JsonLdConceptConverter
from spotterbase.concept_graphs.oa_support import OA_JSONLD_CONTEXT
from spotterbase.concept_graphs.sb_support import SB_JSONLD_CONTEXT
from spotterbase.rdf import to_rdflib
from spotterbase.test.mixins import GraphTestMixin


class TestAnnotationSerialization(GraphTestMixin, unittest.TestCase):
    def test_jsonld_is_same_as_generated_triples(self):
        package_root = Path(__file__).parent.parent
        with open(package_root / 'resources' / 'sb-context.jsonld') as fp:
            sb_context = json.load(fp)
        converter = JsonLdConceptConverter(
            contexts=[OA_JSONLD_CONTEXT, SB_JSONLD_CONTEXT],
            concept_resolver=ANNOTATION_CONCEPT_RESOLVER,
        )
        for path in [
            package_root.parent / 'doc' / 'source' / 'codesnippets' / 'example-annotation.jsonld',
            package_root.parent / 'doc' / 'source' / 'codesnippets' / 'example-target.jsonld',
        ]:
            with self.subTest(file=path):
                with open(path) as fp:
                    jsonld = json.load(fp)
                # my_graph = to_rdflib.Converter.convert_to_graph(class_.from_json(jsonld).to_triples())
                my_graph = to_rdflib.Converter.convert_to_graph(converter.json_ld_to_concept(jsonld).to_triples())
                jsonld['@context'] = ['http://www.w3.org/ns/anno.jsonld', sb_context]
                json_ld_graph = rdflib.Graph().parse(data=json.dumps(jsonld), format='json-ld')

                with open('/tmp/graphs.txt', 'w') as fp:
                    fp.write('MY GRAPH\n')
                    fp.write(my_graph.serialize(format='nt'))
                    fp.write('\n\n\nJSON-LD GRAPH\n')
                    fp.write(json_ld_graph.serialize(format='nt'))

                self.assert_equal_graphs(
                    my_graph,
                    json_ld_graph,
                )
