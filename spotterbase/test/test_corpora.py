import unittest

from spotterbase.corpora.interface import Corpus, Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.corpora.test_corpus import TEST_CORPUS_URI
from spotterbase.plugins.arxiv.arxmliv import ArXMLivUris
from spotterbase.rdf.uri import Uri


class TestDnm(unittest.TestCase):
    def test_resolver_get_corpus(self):
        self.assertIsInstance(Resolver.get_corpus(TEST_CORPUS_URI), Corpus)
        self.assertIsInstance(Resolver.get_corpus(ArXMLivUris.get_corpus_uri('08.2019')), Corpus)
        self.assertIsNone(Resolver.get_corpus(Uri('http://not-a-real-corpus.org')))

    def test_resolver_get_document(self):
        self.assertIsInstance(Resolver.get_document(TEST_CORPUS_URI / 'paperA'), Document)
        self.assertIsNone(Resolver.get_document(Uri('http://not-a-real-corpus.org/not-a-real-document')))
