from __future__ import annotations

import abc
import dataclasses
from typing import TypeVar

from spotterbase.annotations.dom_range import DomRange
from spotterbase.dnm.l_str import LStr


class Dnm(abc.ABC):
    @abc.abstractmethod
    def get_dnm_str(self) -> DnmStr:
        raise NotImplementedError()

    @abc.abstractmethod
    def offset_to_range(self, offset: int) -> DomRange:
        raise NotImplementedError()


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
        self.to = to   # NOTE: `to` is included in the range (unlike DomRange etc.)

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

    def normalize_spaces(self) -> DnmStr:
        """ replace sequences of whitespaces with a single one."""
        # TODO: clean the code up and potentially move it into LStr
        new_string = ''
        new_backrefs = []
        for i in range(len(self)):
            if not self.string[i].isspace():
                new_string += self.string[i]
                new_backrefs.append(self.backrefs[i])
            else:
                if not (i >= 1 and self.string[i - 1].isspace()):
                    new_string += ' '
                    new_backrefs.append(self.backrefs[i])
        return DnmStr(string=new_string, backrefs=new_backrefs, dnm=self.dnm)
