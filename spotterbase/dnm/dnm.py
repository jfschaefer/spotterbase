from __future__ import annotations

import abc
import bisect
import dataclasses
from typing import TypeVar, Sequence

from lxml.etree import _Element

from spotterbase.corpora.interface import Document
from spotterbase.dnm.l_str import LStr
from spotterbase.rdf import Uri
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


@dataclasses.dataclass
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


@dataclasses.dataclass(slots=True, frozen=True)
class DnmRange:
    """ A slice of a DNM (more light-weight than creating a sub-DNM) """
    from_: int
    to: int    # not inclusive (for consistency)
    dnm: Dnm

    def to_dom(self) -> DomRange:
        return DomRange(
            self.dnm.dnm_meta.offset_converter.get_dom_point(self.dnm.start_refs[self.from_], OffsetType.NodeText),
            self.dnm.dnm_meta.offset_converter.get_dom_point(self.dnm.end_refs[self.to - 1], OffsetType.NodeText),
        )
        # return DomRange(self.from_.to_dom(), self.to.to_dom())

    def get_offsets(self) -> tuple[int, int]:
        return self.dnm.start_refs[self.from_], self.dnm.end_refs[self.to - 1]

    def as_dnm(self) -> Dnm:
        return self.dnm[self.from_:self.to]


@dataclasses.dataclass
class DnmMeta:
    dom: _Element
    offset_converter: OffsetConverter
    selector_converter: SelectorConverter
    uri: Uri


DnmT = TypeVar('DnmT', bound='Dnm')


class Dnm(LStr):
    __slots__ = LStr.__slots__ + ('dnm_meta',)
    dnm_meta: DnmMeta

    def __init__(self, string: str, start_refs: Sequence[int], end_refs: Sequence[int], dnm_meta: DnmMeta):
        LStr.__init__(self, string, start_refs, end_refs)
        self.dnm_meta = dnm_meta

    def dnm_range_from_dom_range(self, dom_range: DomRange) -> tuple[DnmRange, DnmMatchIssues]:
        required_range: DomOffsetRange = self.dnm_meta.offset_converter.convert_dom_range(dom_range)
        start_index = bisect.bisect(self.end_refs, required_range.start)
        end_index = bisect.bisect(self.start_refs, required_range.end - 1) - 1
        # print('trying', self.end_refs, required_range.end, end_index)

        return (
            DnmRange(start_index, end_index + 1, self),
            DnmMatchIssues(
                dom_start_earlier=required_range.start < self.start_refs[start_index],
                dom_end_later=required_range.end > self.end_refs[end_index],
                dom_start_later=required_range.start > self.start_refs[start_index],
                dom_end_earlier=required_range.end < self.end_refs[end_index]
            )
        )

    def new(self: DnmT, new_string: str, new_start_refs: Sequence[int], new_end_refs: Sequence[int]) -> DnmT:
        return self.__class__(new_string, new_start_refs, new_end_refs, self.dnm_meta)

    def as_range(self) -> DnmRange:
        return DnmRange(0, len(self.string), self)
