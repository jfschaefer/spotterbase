import io
import json
import tempfile
import unittest
from pathlib import Path

import rdflib
from lxml import etree

from spotterbase.model_core.sb import SB_JSONLD_CONTEXT
from spotterbase.rdf.literal import Literal, HtmlFragment
from spotterbase.rdf.bnode import BlankNode, counter_factory
from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri
from spotterbase.rdf.namespace_collection import NameSpaceCollection
from spotterbase.rdf.serializer import TurtleSerializer, NTriplesSerializer, FileSerializer
from spotterbase.rdf.vocab import RDF, XSD
from spotterbase.utils.resources import RESOURCES_DIR


class MyVocab(Vocabulary):
    NS = NameSpace('http://example.com/myvocab', 'mv:')
    thingA: Uri
    thingB: Uri
    someClass: Uri
    someRel: Uri


class TestRdf(unittest.TestCase):
    def test_turtle_serialize(self):
        stringio = io.StringIO()
        serializer = TurtleSerializer(stringio)
        serializer.write_comment('this is a comment for turtle')
        serializer.add_from_iterable([
            (MyVocab.thingA, RDF.type, MyVocab.someClass),
            (MyVocab.thingB, RDF.type, MyVocab.someClass),
            (MyVocab.thingA, MyVocab.someRel, MyVocab.thingA),
            (MyVocab.thingA, MyVocab.someRel, MyVocab.thingB),
            (MyVocab.thingA, MyVocab.someRel, Literal('some string', XSD.string)),
        ])
        serializer.write_comment('this is another comment for turtle')
        serializer.flush()
        self.assertEqual(stringio.getvalue().strip(), '''
# this is a comment for turtle
@prefix mv: <http://example.com/myvocab> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
mv:thingB a mv:someClass .
mv:thingA a mv:someClass ;
  mv:someRel mv:thingA,
    mv:thingB,
    "some string" .
# this is another comment for turtle
'''.strip())

    def test_namespacify(self):
        ns1 = NameSpace('http://example.com/ns1/', 'ns1:')
        ns2 = NameSpace('http://example.com/ns2/', 'ns2:')
        ns12 = NameSpace('http://example.com/ns1/2/', 'ns12:')
        collection = NameSpaceCollection([ns1, ns2, ns12])
        self.assertEqual(format(collection.namespacify('http://example.com/ns1/2/abc'), ':'), 'ns12:abc')
        self.assertEqual(format(collection.namespacify('http://example.com/ns3'), ':'),
                         '<http://example.com/ns3>')
        self.assertEqual(format(collection.namespacify('http://example.com/ns1/foo'), ':'), 'ns1:foo')

    def test_uri(self):
        uri = Uri('http://example.com/abc', NameSpace('http://example.com/', 'ex:'))
        self.assertEqual(format(uri, ':'), 'ex:abc')
        self.assertEqual(format(uri, '<>'), '<http://example.com/abc>')
        self.assertEqual(str(uri), 'http://example.com/abc')

    def test_ntriples_serialize(self):
        BlankNode.overwrite_factory(counter_factory(1))   # for reproducibility
        stringio = io.StringIO()
        serializer = NTriplesSerializer(stringio)
        serializer.write_comment('this is a comment for ntriples')
        serializer.add_from_iterable([
            (MyVocab.thingA, MyVocab.someRel, MyVocab.thingA),
            (MyVocab.thingA, MyVocab.someRel, Literal('some string', XSD.string)),
            (BlankNode(), MyVocab.someRel, Literal('some string', XSD.string)),
        ])
        serializer.write_comment('this is another comment for ntriples')
        serializer.flush()
        self.assertEqual(stringio.getvalue().strip(), '''
# this is a comment for ntriples
<http://example.com/myvocabthingA> <http://example.com/myvocabsomeRel> <http://example.com/myvocabthingA> .
<http://example.com/myvocabthingA> <http://example.com/myvocabsomeRel> "some string" .
_:1 <http://example.com/myvocabsomeRel> "some string" .
# this is another comment for ntriples
'''.strip())

    def test_file_serializer(self):
        for filename, output in [
            ('test.ttl', '''
@prefix mv: <http://example.com/myvocab> .
mv:thingA mv:someRel mv:thingA,
    mv:thingB .
# test test'''),
            ('test.nt', '''
<http://example.com/myvocabthingA> <http://example.com/myvocabsomeRel> <http://example.com/myvocabthingA> .
<http://example.com/myvocabthingA> <http://example.com/myvocabsomeRel> <http://example.com/myvocabthingB> .
# test test
''')]:
            with tempfile.TemporaryDirectory() as tmpdirname:
                testfile = Path(tmpdirname) / filename
                with FileSerializer(testfile) as serializer:
                    serializer.add_from_iterable([
                        (MyVocab.thingA, MyVocab.someRel, MyVocab.thingA),
                        (MyVocab.thingA, MyVocab.someRel, MyVocab.thingB),
                    ])
                    serializer.write_comment('test test')
                with open(testfile) as fp:
                    self.assertEqual(fp.read().strip(), output.strip())

    def test_literal(self):
        self.assertEqual(Literal.from_py_val(42).to_py_val(), 42)
        self.assertEqual(Literal.from_py_val(4.5).to_ntriples(),
                         '\"4.500000E+00\"^^<http://www.w3.org/2001/XMLSchema#double>')
        l = Literal('[2,3]', datatype=Uri('http://example.org/listdatatype'))
        with self.assertRaises(NotImplementedError):
            l.to_py_val()
        with self.assertRaises(TypeError):
            Literal.from_py_val([2, 3])

    def test_rdflib_literal_conversion(self):
        rdflib_literal = rdflib.Literal(42, datatype=rdflib.XSD.integer)
        my_literal = Literal.from_rdflib(rdflib_literal)
        self.assertEqual(my_literal.datatype, XSD.integer)
        self.assertEqual(my_literal.to_py_val(), 42)

    def test_context_generation(self):
        updated_sb_context = {'@context': SB_JSONLD_CONTEXT.export_to_json()}
        SB_CONTEXT_FILE: Path = RESOURCES_DIR / 'sb-context.jsonld'
        with open(SB_CONTEXT_FILE, 'r') as fp:
            sb_context = json.load(fp)
        import spotterbase.model_core.update_sb_context_file
        self.assertEqual(sb_context, updated_sb_context,
                         msg='\n The "sb-context.jsonld" file is not up-to-date. '
                             f'Please re-run the "{spotterbase.model_core.update_sb_context_file.__name__}" module')

    def test_html_literal(self):
        f = HtmlFragment(etree.parse(io.StringIO('<a><b>x</b>y<c>z</c></a>')).getroot(), wrapped_in_div=False)
        l = Literal.from_py_val(f)
        self.assertEqual(l.to_turtle(),
                         '"<a><b>x</b>y<c>z</c></a>"^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML>')
