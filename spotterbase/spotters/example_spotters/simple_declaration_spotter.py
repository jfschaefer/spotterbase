import logging
import re
from datetime import datetime
from typing import Iterable, Optional, Iterator

from lxml.etree import _Element, _ElementTree

import spotterbase.dnm_nlp.xml_match as xm
from spotterbase import __version__
from spotterbase.corpora.interface import Document
from spotterbase.dnm.defaults import ARXMLIV_STANDARD_DNM_FACTORY_SIMPLE
from spotterbase.dnm.dnm import Dnm
from spotterbase.dnm.range_subst import RangeSubstituter
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.annotation_creator import SpotterRun
from spotterbase.model_core.sb import SB
from spotterbase.model_core.target import FragmentTarget
from spotterbase.model_extra.declarations import Identifier, IdentifierDeclaration, IdentifierOccurrence, \
    PolarityVocab, POLARITY_TAG_SET, POLARITY_TAGS, IdentifierTypeRestriction
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import OA, DCTerms
from spotterbase.selectors.dom_range import DomRange
from spotterbase.sparql.sb_sparql import get_data_endpoint
from spotterbase.spotters.spotter import UriGeneratorMixin, Spotter, SpotterContext

logger = logging.getLogger(__name__)


def get_marked_concepts_substituter(doc_uri: Uri) -> RangeSubstituter[Uri]:
    query = f'''
SELECT DISTINCT ?target ?start ?end WHERE {{
    VALUES ?creator {{ <urn:uuid:c84b5401-4cc1-4c23-8e60-df0771d31ef8> }} .
    ?target {OA.hasSource:<>} {doc_uri:<>} .
    ?target {OA.hasSelector:<>} [
        a {SB.OffsetSelector:<>} ;
        {OA.start:<>} ?start ;
        {OA.end:<>} ?end
    ] .
    ?anno {OA.hasTarget:<>} ?target .
    ?anno {DCTerms.creator:<>} ?creator .
}}
'''
    results = get_data_endpoint().query(query)
    l: list[tuple[tuple[int, int], tuple[str, Uri]]] = []
    for result in results:
        target_uri = result['target']
        assert isinstance(target_uri, Uri)
        start: int = result['start'].to_py_val()  # type: ignore
        end: int = result['end'].to_py_val()  # type: ignore
        l.append(((start, end), ('SpottedConcept', target_uri)))
    if not l:
        return RangeSubstituter(l)

    # deal with overlapping things. E.g. 'positive integer' and 'integer'
    l.sort()
    l2 = [l[0]]
    for e in l[1:]:
        if e[0][0] < l2[-1][0][1]:
            continue
        l2.append(e)

    return RangeSubstituter(l2)


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
        # tree = etree.parse(document.open(), parser=etree.HTMLParser())  # type: ignore
        tree = document.get_html_tree(cached=True)
        selector_converter = document.get_selector_converter()
        dnm = ARXMLIV_STANDARD_DNM_FACTORY_SIMPLE.dnm_from_document(document).lower()

        # regex_univ = re.compile('((let)|(for (every|all))|(where)) (?P<m>mathnode)')
        regex_univ1 = re.compile('(for ((every)|(all)|(any))) (?P<c>SpottedConcept)?(?P<m>mathnode)')
        regex_univ2 = re.compile('((let)|(where)) (?P<m>mathnode)( ((is)|(be)) an? (?P<c>SpottedConcept))?')
        regex_exist = re.compile('((for some)|(there is an?)) (?P<c>SpottedConcept)?(?P<m>mathnode)')

        range_substitutor = get_marked_concepts_substituter(document.get_uri())
        dnm = range_substitutor.apply(dnm)

        for para_node in get_para_nodes(tree):
            para_dnm: Dnm = dnm.sub_dnm_from_dom_range(DomRange.from_node(para_node))[0]

            for is_universal, regex in [(True, regex_univ1), (True, regex_univ2), (False, regex_exist)]:
                for m in regex.finditer(str(para_dnm)):
                    id_node = get_identifier_from_node(
                        para_dnm[m.start('m')].to_dom().get_containing_node()
                    )
                    if id_node is None:
                        continue

                    # part 1: identifier declaration
                    uri = next(uri_generator)
                    identifier = Identifier(uri('identifier'), id_string=''.join(id_node.itertext()))   # type: ignore
                    yield from identifier.to_triples()
                    id_decl_target = FragmentTarget(
                        uri('target'), source=document.get_uri(),
                        selectors=selector_converter.dom_to_selectors(DomRange.from_node(id_node))
                    )
                    yield from id_decl_target.to_triples()
                    yield from Annotation(
                        uri('anno'), target_uri=id_decl_target.uri, creator_uri=self.ctx.run_uri,
                        body=IdentifierDeclaration(
                            declares=identifier.uri,
                            polarity=PolarityVocab.universal if is_universal else PolarityVocab.existential
                        )
                    ).to_triples()

                    if m.group('c'):
                        uri = next(uri_generator)
                        # part 2: type constraint
                        # dnm_range = DnmRange(m.start('c'), m.end('c'), para_dnm)
                        a = para_dnm.get_start_refs()[m.start('c') + 1]  # should all have the same back refs
                        b = para_dnm.get_start_refs()[m.start('c') + 1]
                        target = range_substitutor.substitution_values[(a, b)]
                        yield from Annotation(
                            uri('anno'), target_uri=target, creator_uri=self.ctx.run_uri,
                            body=IdentifierTypeRestriction(restricts=identifier.uri)
                        ).to_triples()

                    # part 3: identifier occurrences
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
                                selectors=selector_converter.dom_to_selectors(DomRange.from_node(matched_node))
                            )
                            yield from id_occ_target.to_triples()
                            yield from Annotation(
                                uri('anno'), target_uri=id_occ_target.uri,
                                body=IdentifierOccurrence(occurrence_of=identifier.uri), creator_uri=self.ctx.run_uri
                            ).to_triples()


if __name__ == '__main__':
    from spotterbase.spotters import spotter_runner

    spotter_runner.auto_run_spotter(SimpleDeclarationSpotter)
