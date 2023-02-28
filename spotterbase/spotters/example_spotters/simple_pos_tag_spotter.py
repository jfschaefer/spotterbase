import itertools
import json
from typing import Iterator

import nltk.tag
from lxml import etree

from spotterbase import config_loader
from spotterbase.annotations.annotation import Annotation
from spotterbase.annotations.concepts import ANNOTATION_CONCEPT_RESOLVER
from spotterbase.annotations.selector_converter import SelectorConverter
from spotterbase.annotations.tag_body import SimpleTagBody, Tag, TagSet
from spotterbase.annotations.target import FragmentTarget
from spotterbase.concept_graphs.concept_graph import Concept
from spotterbase.concept_graphs.jsonld_support import JsonLdConceptConverter
from spotterbase.concept_graphs.oa_support import OA_JSONLD_CONTEXT
from spotterbase.concept_graphs.sb_support import SB_JSONLD_CONTEXT
from spotterbase.corpora.arxmliv import ArXMLivUris
from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.dnm import DnmStr
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators
from spotterbase.dnm_nlp.sentence_tokenizer import sentence_tokenize
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.rdf.uri import Uri
from spotterbase.sb_vocab import SB
from spotterbase.spotters.spotter import Spotter, UriGeneratorMixin

_univ_pos_tags: Uri = SB.NS['universal-pos-tags']


class SimplePosTagSpotter(UriGeneratorMixin, Spotter):
    spotter_short_id = 'spostag'

    tag_set = TagSet(uri=_univ_pos_tags, label='Universal Part-Of-Speech Tagset',
                     comment='See https://arxiv.org/abs/1104.2086 for more information')

    tags: dict[str, Tag] = {
        tag: Tag(uri=_univ_pos_tags + f'#{tag}', label=tag, belongs_to=_univ_pos_tags, comment=comment)
        for tag, comment in [
            ('VERB', 'verbs (all tenses and modes)'),
            ('NOUN', 'nouns (common and proper)'),
            ('PRON', 'pronouns'),
            ('ADJ', 'adjectives'),
            ('ADV', 'adverbs'),
            ('ADP', 'adpositions (prepositions and postpositions)'),
            ('CONJ', 'conjunctions'),
            ('DET', 'determiners'),
            ('NUM', 'cardinal numbers'),
            ('PRT', 'particles or other function words'),
            ('X', 'other: foreign words, typos, abbreviations'),
            ('.', 'punctuation'),
        ]
    }

    tag_set.tags = [tag.uri for tag in tags.values()]

    def process_document(self, document: Document) -> Iterator[Concept]:
        uri_generator = self.get_uri_generator_for(document)

        tree = etree.parse(document.open(), parser=etree.HTMLParser())  # type: ignore
        dnm = TokenBasedDnm.from_token_generator(tree, DefaultGenerators.ARXMLIV_TEXT_ONLY)
        dnm_str: DnmStr = dnm.get_dnm_str()
        selector_converter = SelectorConverter(document.get_uri(), tree.getroot())

        for sentence in sentence_tokenize(dnm_str):
            words = word_tokenize(sentence)
            pos_tagged = nltk.tag.pos_tag([str(word) for word in words], tagset='universal')
            assert len(words) == len(pos_tagged)
            for dnm_word, tagged_word in zip(words, pos_tagged):
                uri = next(uri_generator)
                target = FragmentTarget(uri('target'), document.get_uri(),
                                        selector_converter.dom_to_selectors(dnm_word.as_range().to_dom()))
                yield target
                yield Annotation(
                    uri=uri('anno'),
                    target_uri=target.uri,
                    body=SimpleTagBody(self.tags[tagged_word[1]].uri),
                    creator_uri=self.ctx.run_uri,
                )


if __name__ == '__main__':
    def test_run():
        config_loader.auto()
        ctx = SimplePosTagSpotter.setup_run()[0]
        spotter = SimplePosTagSpotter(ctx)
        document = Resolver.get_document(ArXMLivUris.get_corpus_uri('2020') + '1910.06709')
        assert document is not None, 'Document not found'
        concepts = list(spotter.process_document(document))
        with document.open() as doc_fp:
            with open('/tmp/document.html', 'wb') as out_fp:
                out_fp.write(doc_fp.read())
        jsonld_converter = JsonLdConceptConverter(contexts=[OA_JSONLD_CONTEXT, SB_JSONLD_CONTEXT],
                                                  concept_resolver=ANNOTATION_CONCEPT_RESOLVER)
        with open('/tmp/annotations.json', 'w') as fp:
            json.dump([jsonld_converter.concept_to_json_ld(concept) for concept in itertools.chain(
                concepts, (spotter.tag_set,), spotter.tags.values())], fp, indent=4)

    test_run()
