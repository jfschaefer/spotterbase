import logging
import re
from datetime import datetime
from typing import Iterable, Optional, Iterator

from lxml import etree
from lxml.etree import _Element, _ElementTree

from spotterbase import __version__
import spotterbase.dnm_nlp.xml_match as xm
from spotterbase.anno_core.annotation import Annotation
from spotterbase.anno_core.annotation_creator import SpotterRun
from spotterbase.selectors.dom_range import DomPoint
from spotterbase.selectors.selector_converter import SelectorConverter
from spotterbase.anno_core.target import FragmentTarget
from spotterbase.corpora.interface import Document
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.uri import Uri
from spotterbase.anno_core.sb import SB
from spotterbase.anno_extra.declarations import Identifier, IdentifierDeclaration, IdentifierOccurrence, \
    PolarityVocab, POLARITY_TAG_SET, POLARITY_TAGS
from spotterbase.spotters.spotter import UriGeneratorMixin, Spotter, SpotterContext

logger = logging.getLogger(__name__)


def get_para_nodes(tree: _ElementTree) -> Iterable[_Element]:
    para_nodes = tree.xpath('//div[@class="ltx_para"]')
    if not para_nodes:
        logger.warning('No paragraphs found. Maybe the document does not belong to the arXMLiv corpus? '
                       'Falling back to more naive implementation')
        para_nodes = tree.xpath('//p')

    assert isinstance(para_nodes, list)
    para_node_set: set = set(para_nodes)

    for para_node in para_node_set:
        assert isinstance(para_node, _Element)

        # make sure we only use the lowest level of paragraphs
        isokay: bool = True
        node = para_node.getparent()
        while node is not None:
            if node in para_node_set:
                isokay = False
            node = node.getparent()

        if isokay:
            yield para_node


def _get_id_matcher():
    identifier = (xm.tag('mi') | xm.tag('msub') / xm.seq(xm.tag('mi'), xm.any_tag)) ** 'identifier'
    relation = xm.tag('mo').with_text(
        '[' + ''.join({'<', '>', '≪', '≫', '≥', '⩾', '≤', '⩽', '∼', '≲', '≳', '⊆', '∈', '≠', '⊇'}) + ']'
    )
    return (xm.tag('math') / xm.tag('semantics') /
            (identifier | (xm.tag('mrow') / xm.seq(identifier, relation, xm.any_tag))))


identifier_matcher = _get_id_matcher()


def get_identifier_from_node(node: _Element) -> Optional[_Element]:
    matches = list(identifier_matcher.match(node))
    if not matches:
        return None
    assert len(matches) == 1
    match = matches[0]
    assert match.label == 'identifier'
    return match.node


def node_equal(a: _Element, b: _Element) -> bool:
    # note: some attributes are relevant as well
    if a.tag != b.tag or a.text != b.text:
        return False
    a_children = list(a.iterchildren())
    b_children = list(b.iterchildren())
    if len(a_children) != len(b_children):
        return False
    for ac, bc in zip(a_children, b_children):
        if not node_equal(ac, bc):
            return False
    return True


def find_node_matches(node: _Element, goal: _Element) -> Iterator[_Element]:
    if node_equal(node, goal):
        yield node
    for child in node.iterchildren():
        yield from find_node_matches(child, goal)


class SimpleDeclarationSpotter(UriGeneratorMixin, Spotter):
    spotter_short_id = 'sdecl'

    @classmethod
    def setup_run(cls, **kwargs) -> tuple[SpotterContext, TripleI]:
        ctx = SpotterContext(Uri.uuid())

        def triple_gen() -> TripleI:
            yield from POLARITY_TAG_SET.to_triples()
            for tag in POLARITY_TAGS:
                yield from tag.to_triples()
            yield from SpotterRun(
                uri=ctx.run_uri,
                spotter_uri=SB.NS['spotter/simple-declaration-spotter'],
                spotter_version=__version__,
                date=datetime.now(),
            ).to_triples()

        return ctx, triple_gen()

    def process_document(self, document: Document) -> TripleI:
        uri_generator = self.get_uri_generator_for(document)
        tree = etree.parse(document.open(), parser=etree.HTMLParser())  # type: ignore

        selector_converter = SelectorConverter(document.get_uri(), tree.getroot())
        dnm = TokenBasedDnm.from_token_generator(tree, DefaultGenerators.ARXMLIV_TEXT_ONLY,
                                                 selector_converter.offset_converter)

        regex_univ = re.compile('((let)|(for (every|all))|(where)) (?P<m>mathnode)')
        regex_exist = re.compile('((for some)|(there is an?)) (?P<m>mathnode)')

        for para_node in get_para_nodes(tree):
            para_range = dnm.dom_range_to_dnm_range(DomPoint(para_node).as_range())[0]
            para_string = dnm.get_dnm_str(para_range).lower()

            for is_universal, regex in [(True, regex_univ), (False, regex_exist)]:
                for m in regex.finditer(para_string.string):
                    id_node = get_identifier_from_node(
                        para_string[m.start('m')].as_range().to_dom().get_containing_node()
                    )
                    if id_node is None:
                        continue

                    # uri = next(uri_generator)
                    # decl_phrase_target = FragmentTarget(
                    #     uri('target'), source=document.get_uri(),
                    #     selectors=selector_converter.dom_to_selectors(
                    #         para_string[m.start():m.end()].as_range().to_dom()))

                    # part 1: identifier declaration
                    uri = next(uri_generator)
                    identifier = Identifier(uri('identifier'))
                    yield from identifier.to_triples()
                    id_decl_target = FragmentTarget(
                        uri('target'), source=document.get_uri(),
                        selectors=selector_converter.dom_to_selectors(DomPoint(id_node).as_range())
                    )
                    yield from id_decl_target.to_triples()
                    yield from Annotation(
                        uri('anno'), target_uri=id_decl_target.uri, creator_uri=self.ctx.run_uri,
                        body=IdentifierDeclaration(
                            declares=identifier.uri,
                            polarity=PolarityVocab.universal if is_universal else PolarityVocab.existential
                        )
                    ).to_triples()

                    # part 2: identifier occurrences
                    math_nodes_in_para = para_node.xpath('.//math')
                    assert isinstance(math_nodes_in_para, list)
                    for math_node in math_nodes_in_para:
                        assert isinstance(math_node, _Element)
                        for matched_node in find_node_matches(math_node, id_node):
                            if matched_node == id_node:
                                continue
                            uri = next(uri_generator)
                            id_occ_target = FragmentTarget(
                                uri('target'), source=document.get_uri(),
                                selectors=selector_converter.dom_to_selectors(DomPoint(matched_node).as_range())
                            )
                            yield from id_occ_target.to_triples()
                            yield from Annotation(
                                uri('anno'), target_uri=id_occ_target.uri,
                                body=IdentifierOccurrence(occurrence_of=identifier.uri), creator_uri=self.ctx.run_uri
                            ).to_triples()


if __name__ == '__main__':
    from spotterbase.spotters import spotter_runner

    spotter_runner.main(SimpleDeclarationSpotter)
