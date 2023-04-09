import itertools
from typing import Optional

from lxml.etree import _Element

from spotterbase.dnm.dnm import DnmFactory, Dnm, DnmMeta
from spotterbase.dnm.xml_util import get_node_classes


class SimpleDnmFactory(DnmFactory):
    def __init__(self, nodes_to_replace: Optional[dict[str, str]] = None,
                 classes_to_replace: Optional[dict[str, str]] = None):
        self.nodes_to_replace = nodes_to_replace or {}
        self.classes_to_replace = classes_to_replace or {}

    def make_dnm_from_meta(self, dnm_meta: DnmMeta) -> Dnm:
        start_refs: list[int] = []
        end_refs: list[int] = []
        strings: list[str] = []
        offset_converter = dnm_meta.offset_converter

        def recurse(node: _Element):
            """ processes both the node and its tail """
            offs = offset_converter.get_offset_data(node)

            replacement = self._get_replacement(node)
            if replacement is not None:
                if replacement != '':       # empty replacement -> skip node
                    strings.append(replacement)
                    start_refs.extend(itertools.repeat(offs.node_text_offset_before, len(replacement)))
                    end_refs.extend(itertools.repeat(offs.node_text_offset_after, len(replacement)))

            else:   # no replacement -> recurse
                if node.text:
                    text = node.text
                    strings.append(text)
                    start_refs.extend(range(offs.node_text_offset_before + 1,
                                            offs.node_text_offset_before + len(text) + 1))
                    end_refs.extend(range(offs.node_text_offset_before + 2,
                                          offs.node_text_offset_before + len(text) + 2))
                for child in node:
                    recurse(child)

            if node.tail:
                tail = node.tail
                strings.append(tail)
                start_refs.extend(range(offs.node_text_offset_after,
                                        offs.node_text_offset_after + len(tail)))
                end_refs.extend(range(offs.node_text_offset_after + 1,
                                      offs.node_text_offset_after + len(tail) + 1))

        recurse(dnm_meta.dom)

        return Dnm(''.join(strings), start_refs=start_refs, end_refs=end_refs, dnm_meta=dnm_meta)

    def _get_replacement(self, node: _Element) -> Optional[str]:
        if node.tag in self.nodes_to_replace:
            return self.nodes_to_replace[node.tag]
        for c in get_node_classes(node):
            if c in self.classes_to_replace:
                return self.classes_to_replace[c]
        return None


ARXMLIV_STANDARD_DNM_FACTORY = SimpleDnmFactory(
    nodes_to_replace={'head': '', 'figure': '', 'math': 'MathNode'},
    classes_to_replace={
        # to ignore
        'ltx_bibliography': '', 'ltx_page_footer': '', 'ltx_dates': '', 'ltx_authors': '',
        'ltx_role_affiliationtext': '', 'ltx_tag_equation': '', 'ltx_classification': '',
        'ltx_tag_section': '', 'ltx_tag_subsection': '', 'ltx_note_mark': '',
        # to replace
        'ltx_equationgroup': 'MathGroup', 'ltx_cite': 'LtxCite',
        'ltx_ref': 'LtxRef', 'ltx_ref_tag': 'LtxRef', 'ltx_equation': 'MathEquation',
    }
)