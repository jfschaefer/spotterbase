import io
import unittest

from spotterbase.rdf.base import Vocabulary, NameSpace, Uri
from spotterbase.rdf.literals import StringLiteral
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import RDF


class MyVocab(Vocabulary):
    NS = NameSpace('http://example.com/myvocab', 'mv:')
    thingA: Uri
    thingB: Uri
    someClass: Uri
    someRel: Uri


class TestRdf(unittest.TestCase):
    def test_serialize(self):
        stringio = io.StringIO()
        serializer = TurtleSerializer(stringio)
        serializer.add_from_iterable([
            (MyVocab.thingA, RDF.type, MyVocab.someClass),
            (MyVocab.thingB, RDF.type, MyVocab.someClass),
            (MyVocab.thingA, MyVocab.someRel, MyVocab.thingA),
            (MyVocab.thingA, MyVocab.someRel, MyVocab.thingB),
            (MyVocab.thingA, MyVocab.someRel, StringLiteral('some string')),
        ])
        serializer.flush()
        self.assertEqual(stringio.getvalue().strip(), '''
@prefix mv: <http://example.com/myvocab> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
mv:thingB a mv:someClass .
mv:thingA a mv:someClass ;
  mv:someRel mv:thingA,
    mv:thingB,
    'some string' .'''.strip())

    def test_uri(self):
        uri = Uri('abc', NameSpace('http://example.com/', 'ex:'))
        self.assertEqual(format(uri, ':'), 'ex:abc')
        self.assertEqual(format(uri, '<>'), '<http://example.com/abc>')
        self.assertEqual(str(uri), 'http://example.com/abc')
