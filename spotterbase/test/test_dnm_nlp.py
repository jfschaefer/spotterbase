import io
import unittest

from lxml import etree

from spotterbase.dnm.simple_dnm_factory import SimpleDnmFactory
from spotterbase.dnm_nlp.sentence_tokenizer import sentence_tokenize
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize


class TestDnmNlp(unittest.TestCase):
    def test_word_tokenization(self):
        sentence = 'Hello  world. A B Cdef'
        result = word_tokenize(
            sentence,
            keep_as_words=[(sentence.index('A B C'), sentence.index('def'))]
        )
        self.assertEqual(result, ['Hello', 'world', '.', 'A B C', 'def'])

    def test_sentence_tokenization(self):
        def make_dnm(s: str):
            return SimpleDnmFactory().anonymous_dnm_from_node(etree.parse(io.StringIO(s)).getroot())

        dnm = make_dnm('<p>Hello world.</p>')
        self.assertEqual(str(dnm), 'Hello world.')
        dnm = dnm.normalize_spaces()
        self.assertEqual(str(dnm), 'Hello world.')
        sentences = sentence_tokenize(dnm)
        self.assertEqual([str(s) for s in sentences], ['Hello world.'])
