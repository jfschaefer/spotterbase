from __future__ import annotations

import abc
import dataclasses
from collections import defaultdict
from typing import Iterator

from lxml.etree import _Element

from spotterbase.corpora.interface import Document
from spotterbase.dnm.linked_str import LinkedStr
from spotterbase.model_core import FragmentTarget
from spotterbase.model_core.annotation import Annotation
from spotterbase.rdf import Uri, UriLike
from spotterbase.selectors.anno_by_offset import AnnoByOffset
from spotterbase.selectors.dom_range import DomRange
from spotterbase.selectors.offset_converter import OffsetConverter, DomOffsetRange, OffsetType
from spotterbase.selectors.selector_converter import SelectorConverter


class DnmFactory(abc.ABC):
    @abc.abstractmethod
    def make_dnm_from_meta(self, dnm_meta: DnmMeta) -> Dnm:
        ...

    def anonymous_dnm_from_node(self, node: _Element) -> Dnm:
        offset_converter = OffsetConverter(node)
        uri = Uri.uuid()
        return self.make_dnm_from_meta(
            DnmMeta(
                node,
                offset_converter,
                selector_converter=SelectorConverter(
                    uri, node, offset_converter
                ),
                uri=uri
            )
        )

    def dnm_from_document(self, document: Document) -> Dnm:
        return self.make_dnm_from_meta(
            DnmMeta(
                document.get_html_tree(cached=True).getroot(),
                document.get_offset_converter(),
                document.get_selector_converter(),
                document.get_uri(),
            )
        )


@dataclasses.dataclass(slots=True)
class DnmMatchIssues:
    """ When mapping a part of the DOM to the DNM, it might not be a perfect match.
        This class contains more detailed information about the problem.
    """

    # Option 1: The part of the DOM contains something that is not represented in the DNM.
    # This happens if a node is skipped during the DNM generation.
    dom_start_earlier: bool
    dom_end_later: bool

    # Option 2: The DNM result covers more than the original part of the DOM.
    # This happens for example, if we want to get the DNM part corresponding to node x,
    # but during the DNM generation we replaced a parent of x with a string.
    # For example, a <math> node might be replaced with the word MathFormula, and a reference to
    # a part of the formula would result in the whole world MathFormula.
    dom_start_later: bool
    dom_end_earlier: bool

    @property
    def dnm_covers_more(self) -> bool:
        return self.dom_start_later or self.dom_start_earlier

    @property
    def dnm_misses_something(self) -> bool:
        return self.dom_start_earlier or self.dom_end_later


class EmbeddedAnnotations:
    def __init__(self):
        self._annotations: list[tuple[str, DomOffsetRange, Annotation]] = []
        self._annotations_by_unique_replacement: dict[str, int] = {}
        self._category_counters: dict[str, int] = defaultdict(int)
        self.anno_by_offset: AnnoByOffset = AnnoByOffset()

    def insert(self, replacement: str, range_: DomOffsetRange, annotation: Annotation, replacement_unique: bool = True):
        self._annotations.append((replacement, range_, annotation))
        self.anno_by_offset.add_annotation(range_, annotation)
        if replacement_unique:
            if replacement in self._annotations_by_unique_replacement:
                raise ValueError(f'Replacement {replacement} already exists')
            self._annotations_by_unique_replacement[replacement] = len(self._annotations) - 1

    def get_next_replacement_number(self, category: str) -> int:
        self._category_counters[category] += 1
        return self._category_counters[category] - 1

#     def __getitem__(self, item) -> Annotation:
#         return self._annotations_by_unique_replacement[item]
#
#     def __contains__(self, item):
#         return item in self._annotations_by_unique_replacement

    def __iter__(self) -> Iterator[tuple[str, DomOffsetRange, Annotation]]:
        return iter(self._annotations)

    def __bool__(self) -> bool:
        return bool(self._annotations)


@dataclasses.dataclass(frozen=True)
class DnmMeta:
    dom: _Element
    offset_converter: OffsetConverter
    selector_converter: SelectorConverter
    uri: Uri
    embedded_annotations: EmbeddedAnnotations = dataclasses.field(init=False, default_factory=EmbeddedAnnotations)


class Dnm(LinkedStr[DnmMeta]):
    def sub_dnm_from_dom_range(self, dom_range: DomRange) -> tuple[Dnm, DnmMatchIssues]:
        required_range: DomOffsetRange = self.get_meta_info().offset_converter.convert_dom_range(dom_range)
        return self.sub_dnm_from_ref_range(required_range.start, required_range.end)

    def sub_dnm_from_ref_range(self, start_ref: int, end_ref: int) -> tuple[Dnm, DnmMatchIssues]:
        start_index, end_index = self.get_indices_from_ref_range(start_ref, end_ref)

        return (
            self[start_index:end_index],
            DnmMatchIssues(
                dom_start_earlier=start_ref < self.get_start_refs()[start_index],
                dom_end_later=end_ref > self.get_end_refs()[end_index - 1],
                dom_start_later=start_ref > self.get_start_refs()[start_index],
                dom_end_earlier=end_ref < self.get_end_refs()[end_index - 1]
            )
        )

    def to_dom(self) -> DomRange:
        return DomRange(
            self.get_meta_info().offset_converter.get_dom_point(self.get_start_ref(), OffsetType.NodeText),
            self.get_meta_info().offset_converter.get_dom_point(self.get_end_ref(), OffsetType.NodeText),
        )

    def to_dom_offset_range(self) -> DomOffsetRange:
        # TODO: We can optimize this by not converting to DomRange and then back to DomOffsetRange
        return self.get_meta_info().offset_converter.convert_dom_range(self.to_dom())

    def get_embedded_annotations(self) -> list[Annotation]:
        return self.get_meta_info().embedded_annotations.anno_by_offset[self.to_dom_offset_range()]

    def to_fragment_target(self, target_uri: UriLike) -> FragmentTarget:
        return self.get_meta_info().selector_converter.dom_to_fragment_target(target_uri, self.to_dom())
