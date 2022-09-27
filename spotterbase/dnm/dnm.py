from __future__ import annotations
import abc
import dataclasses
from typing import Optional, TypeVar

from lxml.etree import _Element

from spotterbase.dnm.LStr import LStr


class Dnm(abc.ABC):
    def get_dnm_str(self) -> DnmStr:
        raise NotImplementedError()


class DomPoint:
    def __init__(self, node: _Element, *, text_offset: Optional[int] = None, tail_offset: Optional[int] = None):
        assert text_offset is None or tail_offset is None
        self.node = node
        self.text_offset = text_offset
        self.tail_offset = tail_offset


class DomRange:
    def __init__(self, from_: DomPoint, to: DomPoint, to_inclusive: bool = False):
        self.from_ = from_
        self.to = to
        self.to_inclusive = to_inclusive  # `to` is included in range


DnmStrT = TypeVar('DnmStrT', bound='DnmStr')


class DnmStr(LStr):
    def __init__(self, string: str, backrefs: list[int], dnm: Dnm):
        LStr.__init__(self, string, backrefs)
        self.dnm = dnm

    def new(self: DnmStrT, new_string: str, new_backrefs: list[int]) -> DnmStrT:
        return self.__class__(new_string, new_backrefs, self.dnm)


@dataclasses.dataclass
class DnmPoint:
    offset: int
    dnm: Dnm

    def __eq__(self, other) -> bool:
        if not isinstance(other, DnmPoint):
            raise NotImplementedError()
        return self.dnm == other.dnm and self.offset == other.offset


class DnmRange:
    from_: DnmPoint
    to: DnmPoint
    to_inclusive: bool = True
