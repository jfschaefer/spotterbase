""" Rule-based sentence tokenization.

Note that some aspects (e.g. recognition of display math) are arXMLiv-specific,
this could be extended to work better with other corpora as well.
"""

from typing import Optional

from lxml.etree import _Element

from spotterbase.dnm.dnm import Dnm
from spotterbase.dnm.xml_util import get_node_classes


def is_ref_node(node: _Element) -> bool:
    classes = get_node_classes(node)
    return 'ltx_ref' in classes or 'ltx_cite' in classes


def is_display_math(node: _Element) -> bool:
    classes = get_node_classes(node)
    return 'ltx_equation' in classes


def is_in_header(node: _Element) -> bool:
    if node.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
        return True
    parent = node.getparent()
    if parent is not None and is_in_header(parent):
        return True
    return False


def get_surrounding_node(dnm: Dnm) -> _Element:
    return dnm.to_dom().get_containing_node()


def sentence_tokenize(dnm: Dnm) -> list[Dnm]:
    sentences = []
    sent_start = 0
    in_header = False
    for i in range(len(dnm)):
        new_sent_start: Optional[int] = None
        if normal_end_of_sentence(dnm, i):
            new_sent_start = i + 1
        node_containing_i: _Element = get_surrounding_node(dnm[i])
        if not in_header and is_in_header(node_containing_i):
            in_header = True
            new_sent_start = i
        if in_header and not is_in_header(node_containing_i):
            in_header = False
            new_sent_start = i
        if is_display_math(node_containing_i) and not is_display_math(get_surrounding_node(dnm[i + 1])) and \
                dnm.char_at(i + 1).isspace() and dnm.char_at(i + 2).upper():
            new_sent_start = i + 1
        if new_sent_start is not None:
            new_sent = dnm[sent_start:new_sent_start].strip().normalize_spaces()
            if len(new_sent) > 0:
                sentences.append(new_sent)
            sent_start = new_sent_start
    return sentences


def normal_end_of_sentence(dnm: Dnm, i: int) -> bool:
    if dnm.char_at(i) not in {'.', '!', '?'}:
        return False
    isdot = dnm.char_at(i) == '.'
    if isdot and i + 1 < len(dnm) and dnm.char_at(i + 1).islower():
        return False
    if (isdot and
            0 < i < len(dnm) - 1 and
            dnm.char_at(i - 1).isdigit() and
            dnm.char_at(i + 1).isdigit()):
        return False
    if i + 1 < len(dnm) and dnm.char_at(i + 1) == '\xa0':  # followed by a non-breaking space
        return False
    if i + 1 < len(dnm) and dnm.char_at(i + 1) in {',', '.', ':', ';'}:  # "e.g., ", "word..."
        return False
    if i + 2 < len(dnm) and dnm.char_at(i + 1).isspace() and \
            is_ref_node(get_surrounding_node(dnm[i + 2])):
        return False
    return True
