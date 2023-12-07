import unittest

from spotterbase.dnm_nlp.word_tokenizer import word_tokenize


class TestDnmNlp(unittest.TestCase):
    def test_word_tokenization(self):
        sentence = 'Hello  world. A B Cdef'
        result = word_tokenize(
            sentence,
            keep_as_words=[(sentence.index('A B C'), sentence.index('def'))]
        )
        self.assertEqual(result, ['Hello', 'world', '.', 'A B C', 'def'])
