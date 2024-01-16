from datetime import datetime

import nltk.tag

from spotterbase import __version__
from spotterbase.corpora.interface import Document
from spotterbase.dnm.defaults import ARXMLIV_STANDARD_DNM_FACTORY_SIMPLE
from spotterbase.dnm_nlp.sentence_tokenizer import sentence_tokenize
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.model_core import SpotterRun
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.sb import SB
from spotterbase.model_core.body import SimpleTagBody, Tag, TagSet
from spotterbase.model_core.target import FragmentTarget
from spotterbase.plugins.model_extra import SBX
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.uri import Uri
from spotterbase.spotters.spotter import Spotter, UriGeneratorMixin, SpotterContext

_univ_pos_tags: Uri = SB.NS['universal-pos-tags']


class PosTagContext(SpotterContext):
    def __init__(self):
        super().__init__(run_uri=Uri.uuid())

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

    tag_set.tags = [tag.require_uri() for tag in tags.values()]


class SimplePosTagSpotter(UriGeneratorMixin, Spotter):
    spotter_short_id = 'spostag'

    ctx: PosTagContext

    @classmethod
    def setup_run(cls, **kwargs) -> tuple[SpotterContext, TripleI]:
        ctx = PosTagContext()

        def triple_gen() -> TripleI:
            yield from SpotterRun(
                uri=ctx.run_uri,
                spotter_uri=SBX.NS[f'spotters#{cls.spotter_short_id}'],
                spotter_version=__version__,
                date=datetime.now(),
                label='Simple Part-Of-Speech Tagger based on NLTK'
            ).to_triples()
            yield from ctx.tag_set.to_triples()
            for tag in ctx.tags.values():
                yield from tag.to_triples()

        return ctx, triple_gen()

    def process_document(self, document: Document) -> TripleI:
        uri_generator = self.get_uri_generator_for(document)

        dnm = ARXMLIV_STANDARD_DNM_FACTORY_SIMPLE.dnm_from_document(document)
        selector_converter = document.get_selector_converter()

        for sentence in sentence_tokenize(dnm):
            words = word_tokenize(sentence)
            pos_tagged = nltk.tag.pos_tag([str(word) for word in words], tagset='universal')
            assert len(words) == len(pos_tagged)
            for dnm_word, tagged_word in zip(words, pos_tagged):
                uri = next(uri_generator)
                target = FragmentTarget(uri('target'), document.get_uri(),
                                        selector_converter.dom_to_selectors(dnm_word.to_dom()))
                yield from target.to_triples()
                yield from Annotation(
                    uri=uri('anno'),
                    target_uri=target.uri,
                    body=SimpleTagBody(self.ctx.tags[tagged_word[1]].uri),
                    creator_uri=self.ctx.run_uri,
                ).to_triples()


if __name__ == '__main__':
    from spotterbase.spotters import spotter_runner
    spotter_runner.auto_run_spotter(SimplePosTagSpotter)
