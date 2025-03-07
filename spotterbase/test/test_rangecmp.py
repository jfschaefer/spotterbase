import unittest

from spotterbase.evaluate.rangecmp import OffsetEquis, OffsetEquiConfig
from spotterbase.rdf import Uri
from spotterbase.test import InMemoryDocument


class TestDocumentation(unittest.TestCase):
    def test_simple(self):
        document = InMemoryDocument(Uri('file:///test'), b'<html><body>ab<c></c>d</body></html>')
        oe = OffsetEquis.from_doc_simple(document, OffsetEquiConfig(set(), set()))
        self.assertEqual(len(oe.invis), 3)   # tag clusters
