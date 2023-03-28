import nltk.tag
from lxml import etree

from spotterbase.annotations.annotation import Annotation
from spotterbase.annotations.selector_converter import SelectorConverter
from spotterbase.annotations.tag_body import SimpleTagBody, Tag, TagSet
from spotterbase.annotations.target import FragmentTarget
from spotterbase.corpora.interface import Document
from spotterbase.dnm.dnm import DnmStr
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators
from spotterbase.dnm_nlp.sentence_tokenizer import sentence_tokenize
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.uri import Uri
from spotterbase.sb_vocab import SB
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

    tag_set.tags = [tag.uri for tag in tags.values()]


class SimplePosTagSpotter(UriGeneratorMixin, Spotter):
    spotter_short_id = 'spostag'

    ctx: PosTagContext

    @classmethod
    def setup_run(cls, **kwargs) -> tuple[SpotterContext, TripleI]:
        ctx = PosTagContext()

        def triple_gen() -> TripleI:
            yield from ctx.tag_set.to_triples()
            for tag in ctx.tags.values():
                yield from tag.to_triples()

        return ctx, triple_gen()

    def process_document(self, document: Document) -> TripleI:
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
                yield from target.to_triples()
                yield from Annotation(
                    uri=uri('anno'),
                    target_uri=target.uri,
                    body=SimpleTagBody(self.ctx.tags[tagged_word[1]].uri),
                    creator_uri=self.ctx.run_uri,
                ).to_triples()


if __name__ == '__main__':
    from spotterbase.spotters import spotter_runner
    spotter_runner.main(SimplePosTagSpotter)
