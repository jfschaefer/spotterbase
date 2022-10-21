from __future__ import annotations

import abc
import dataclasses
from typing import Optional, TypeVar

from lxml.etree import _Element

from spotterbase.dnm.LStr import LStr


class Dnm(abc.ABC):
    def get_dnm_str(self) -> DnmStr:
        raise NotImplementedError()

    def offset_to_range(self, offset: int) -> DomRange:
        raise NotImplementedError()


class DomPoint:
    def __init__(self, node: _Element, *, text_offset: Optional[int] = None, tail_offset: Optional[int] = None, after: bool = False):
        # after indicates that it refer actually refers to the location right after what is specified
        assert text_offset is None or tail_offset is None
        self.node = node
        self.text_offset = text_offset
        self.tail_offset = tail_offset
        self.after = after

    def is_element(self) -> bool:
        return self.text_offset is None and self.tail_offset is None

    def as_range(self) -> DomRange:
        return DomRange(self, self.as_after())

    def as_after(self) -> DomPoint:
        return DomPoint(self.node, text_offset=self.text_offset, tail_offset=self.tail_offset, after=True)

    def __eq__(self, other):
        if not isinstance(other, DomPoint):
            raise NotImplementedError()
        return self.node == other.node and self.text_offset == other.text_offset and self.tail_offset == other.tail_offset


class DomRange:
    def __init__(self, from_: DomPoint | DomRange, to: DomPoint | DomRange):
        if isinstance(from_, DomPoint):
            self.from_ = from_
        else:
            self.from_ = from_.from_
        if isinstance(to, DomPoint):
            self.to = to
        else:
            self.to = to.to

    def as_point(self) -> Optional[DomPoint]:
        if not self.from_.after and self.from_.as_after() == self.to:
            return self.from_
        return None


@dataclasses.dataclass
class DnmPoint:
    offset: int
    dnm: Dnm

    def __eq__(self, other) -> bool:
        if not isinstance(other, DnmPoint):
            raise NotImplementedError()
        return self.dnm == other.dnm and self.offset == other.offset

    def to_dom(self) -> DomRange:
        return self.dnm.offset_to_range(self.offset)


class DnmRange:
    def __init__(self, from_: DnmPoint, to: DnmPoint):
        self.from_ = from_
        self.to = to

        assert self.to.dnm == self.from_.dnm

    def to_dom(self) -> DomRange:
        return DomRange(self.from_.to_dom(), self.to.to_dom())


DnmStrT = TypeVar('DnmStrT', bound='DnmStr')


class DnmStr(LStr):
    def __init__(self, string: str, backrefs: list[int], dnm: Dnm):
        LStr.__init__(self, string, backrefs)
        self.dnm = dnm

    def new(self: DnmStrT, new_string: str, new_backrefs: list[int]) -> DnmStrT:
        return self.__class__(new_string, new_backrefs, self.dnm)

    def as_range(self) -> DnmRange:
        return DnmRange(DnmPoint(self.backrefs[0], self.dnm), DnmPoint(self.backrefs[-1], self.dnm))
