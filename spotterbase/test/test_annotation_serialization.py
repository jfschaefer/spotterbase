import json
import unittest
from pathlib import Path

import rdflib

from spotterbase.annotations.annotation import Annotation
from spotterbase.rdf import to_rdflib
from spotterbase.test.mixins import GraphTestMixin


class TestAnnotationSerialization(GraphTestMixin, unittest.TestCase):
    def test_jsonld_is_same_as_generated_triples(self):
        package_root = Path(__file__).parent.parent
        with open(package_root / 'resources' / 'sb-context.jsonld') as fp:
            sb_context = json.load(fp)
        for path, class_ in [
            (package_root.parent/'doc'/'source'/'codesnippets'/'example-annotation.jsonld', Annotation)
        ]:
            with self.subTest(file=path, class_=class_):
                with open(path) as fp:
                    jsonld = json.load(fp)
                my_graph = to_rdflib.Converter.convert_to_graph(class_.from_json(jsonld).to_triples())
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

