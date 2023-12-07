import functools
import re
from typing import Callable

from spotterbase.dnm.dnm import DnmFactory, Dnm
from spotterbase.dnm.node_based_dnm_factory import NodeBasedDnmFactory, TextExtractingNP, SkippingNP, ReplacingNP, \
    TokenAfterNodeNP, TextExtractingBlockedNP
from spotterbase.dnm.post_processing_dnm_factory import PostProcessingDnmFactory
from spotterbase.dnm.replacement_pattern import StandardReplacementPattern
from spotterbase.dnm.simple_dnm_factory import SimpleDnmFactory

LINEBREAK_PLACEHOLDER = 'SB-LINEBREAK-PLACEHOLDER'


def whitespace_normalization_post_processing(dnm: Dnm) -> Dnm:
    return dnm.replacements_at_positions(
        [
            (match.start(), match.end(), '\n' if LINEBREAK_PLACEHOLDER in match.group() else ' ')
            for match in re.finditer(f'(\\s|{LINEBREAK_PLACEHOLDER})+', str(dnm))
            if match.group() != ' '
        ],
        positions_are_references=False
    )


def get_arxmliv_dnm_factory(
        *,  # only keyword arguments
        decorate_replacements: bool = True,
        number_replacements: bool = True,
        keep_titles: bool = True,
        keep_replacements_as_annotations: bool = True,
        normalize_white_space: bool = True,
        wrap_replacements_with_spaces: bool = False,
) -> DnmFactory:
    processor = TextExtractingNP()

    base_affix = '@' if decorate_replacements else ''
    extra_space = ' ' if wrap_replacements_with_spaces else ''
    replacement_pattern = StandardReplacementPattern(
        prefix=extra_space + base_affix, infix=':', suffix=base_affix + extra_space
    )

    replacing_np = functools.partial(
        ReplacingNP,
        replacement_pattern=replacement_pattern,
        number_replacements=number_replacements,
        keep_annotation=keep_replacements_as_annotations
    )

    # Skip some nodes
    for tag in ['head', 'script', 'figure']:
        processor.register_tag_processor(tag, SkippingNP())
    for class_ in [
        'ltx_bibliography', 'ltx_page_footer', 'ltx_dates', 'ltx_authors', 'ltx_role_affiliationtext',
        'ltx_tag_equation', 'ltx_classification', 'ltx_tag_section', 'ltx_tag_subsection', 'ltx_note_mark',
        'ar5iv-footer', 'ltx_role_institutetext'
    ]:
        processor.register_class_processor(class_, SkippingNP())
    if not keep_titles:
        if normalize_white_space:
            processor.register_class_processor('ltx_title', TokenAfterNodeNP(LINEBREAK_PLACEHOLDER, SkippingNP()))
        else:
            processor.register_class_processor('ltx_title', SkippingNP())
    elif normalize_white_space:
        processor.register_class_processor(
            'ltx_title', TokenAfterNodeNP(LINEBREAK_PLACEHOLDER, TextExtractingBlockedNP(processor))
        )

    # Replace some nodes
    for tag, category in [('math', 'math node')]:
        processor.register_tag_processor(tag, replacing_np(category=category))
    for class_, category in [
        ('ltx_equationgroup', 'math group'), ('ltx_equation', 'math equation'),
        ('ltx_cite', 'ltx cite'), ('ltx_ref', 'ltx ref'), ('ltx_ref_tag', 'ltx ref')
    ]:
        processor.register_class_processor(class_, replacing_np(category=category))

    # insert linebreaks after ltx_para
    if normalize_white_space:
        processor.register_class_processor(
            'ltx_para', TokenAfterNodeNP(LINEBREAK_PLACEHOLDER, TextExtractingBlockedNP(processor))
        )

    factory: DnmFactory = NodeBasedDnmFactory(processor)
    if normalize_white_space:
        factory = PostProcessingDnmFactory(factory, whitespace_normalization_post_processing)
    return factory


def _default_core_token_processor(token: str) -> str:
    return token.title().replace(' ', '')  # camel case


def get_simple_arxmliv_factory(
        *,  # only keyword arguments
        token_prefix: str = '',
        token_suffix: str = '',
        keep_titles: bool = True,
        core_token_processor: Callable[[str], str] = _default_core_token_processor,
) -> SimpleDnmFactory:
    def tp(token: str) -> str:  # token processor
        return token_prefix + core_token_processor(token) + token_suffix

    node_rules: dict[str, str] = {
        'head': '', 'figure': '', 'script': '',
        'math': tp('math node'),
    }
    class_rules: dict[str, str] = {
        # to ignore
        'ltx_bibliography': '', 'ltx_page_footer': '', 'ltx_dates': '', 'ltx_authors': '',
        'ltx_role_affiliationtext': '', 'ltx_tag_equation': '', 'ltx_classification': '',
        'ltx_tag_section': '', 'ltx_tag_subsection': '', 'ltx_note_mark': '',
        'ar5iv-footer': '', 'ltx_role_institutetext': '',
        # to replace
        'ltx_equationgroup': tp('math group'), 'ltx_equation': tp('math equation'),
        'ltx_cite': tp('ltx cite'), 'ltx_ref': tp('ltx ref'), 'ltx_ref_tag': tp('ltx ref'),
    }
    if not keep_titles:
        class_rules['ltx_title'] = ''
    return SimpleDnmFactory(
        nodes_to_replace=node_rules,
        classes_to_replace=class_rules
    )


ARXMLIV_STANDARD_DNM_FACTORY = get_arxmliv_dnm_factory()
ARXMLIV_STANDARD_DNM_FACTORY_UNNUMBERED = get_arxmliv_dnm_factory(
    decorate_replacements=False,
    number_replacements=False
)
ARXMLIV_STANDARD_DNM_FACTORY_FAST = get_arxmliv_dnm_factory(
    normalize_white_space=False,
    keep_replacements_as_annotations=False
)
ARXMLIV_STANDARD_DNM_FACTORY_SIMPLE = get_simple_arxmliv_factory()
