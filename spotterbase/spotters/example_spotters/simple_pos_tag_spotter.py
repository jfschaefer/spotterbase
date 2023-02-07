import json
from typing import Iterator

import nltk.tag
from lxml import etree

from spotterbase import config_loader
from spotterbase.annotations.annotation import Annotation
from spotterbase.annotations.body import SimpleTagBody
from spotterbase.annotations.selector_converter import SelectorConverter
from spotterbase.annotations.target import FragmentTarget
from spotterbase.corpora.arxmliv import ArXMLivUris
from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.dnm import DnmStr
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators
from spotterbase.dnm_nlp.sentence_tokenizer import sentence_tokenize
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.rdf.base import Uri
from spotterbase.sb_vocab import SB
from spotterbase.spotters.spotter import Spotter, UriGeneratorMixin


class SimplePosTagSpotter(UriGeneratorMixin, Spotter):
    spotter_short_id = 'spostag'

    def process_document(self, document: Document) -> Iterator[Annotation]:
        uri_generator = self.get_uri_generator_for(document)

        tree = etree.parse(document.open(), parser=etree.HTMLParser())   # type: ignore
        dnm = TokenBasedDnm.from_token_generator(tree, DefaultGenerators.ARXMLIV_TEXT_ONLY)
        dnm_str: DnmStr = dnm.get_dnm_str()
        selector_converter = SelectorConverter(document.get_uri(), tree.getroot())

        for sentence in sentence_tokenize(dnm_str):
            words = word_tokenize(sentence)
            pos_tagged = nltk.tag.pos_tag([str(word) for word in words], tagset='universal')
            assert len(words) == len(pos_tagged)
            for dnm_word, tagged_word in zip(words, pos_tagged):
                uri = next(uri_generator)
                yield Annotation(
                    uri=uri('anno'),
                    target=FragmentTarget(uri('target'), document.get_uri(),
                                          selector_converter.dom_to_selectors(dnm_word.as_range().to_dom())),
                    body=SimpleTagBody(SB.NS['pos-tag#' + tagged_word[1]]),
                    creator_uri=self.run_uri
                )


if __name__ == '__main__':
    def test_run():
        config_loader.auto()
        spotter = SimplePosTagSpotter(Uri('http://example.org/mytestrun'))
        document = Resolver.get_document(ArXMLivUris.get_corpus_uri('2020') + '1910.06709')
        assert document is not None, 'Document not found'
        annotations = list(spotter.process_document(document))
        with document.open() as doc_fp:
            with open('/tmp/document.html', 'wb') as out_fp:
                out_fp.write(doc_fp.read())
        with open('/tmp/annotations.json', 'w') as fp:
            json.dump([annotation.to_json() for annotation in annotations], fp, indent=4)
    test_run()
