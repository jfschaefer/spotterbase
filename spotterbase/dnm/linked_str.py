from __future__ import annotations

import bisect
import dataclasses
import re
from typing import TypeVar, Sequence, Generic, Optional

LinkedStr_T = TypeVar('LinkedStr_T', bound='LinkedStr')

_MetaInfoType = TypeVar('_MetaInfoType')


@dataclasses.dataclass(frozen=True, slots=True)
class _RelData(Generic[_MetaInfoType]):
    """ It is expensive to copy references and strings.
    By storing the offsets relative to another LinkedStr, we can save memory and computation time.
    References and strings are now only created on demand.
    This makes the code much more tedious and a bit more error-prone, but should have a substantial performance impact.
    """
    based_on: LinkedStr[_MetaInfoType]
    start_offset: int
    end_offset: int        # exclusive


class LinkedStr(Generic[_MetaInfoType]):
    """ Should be treated as immutable! For optimization, references are used (e.g. when created a sub-linked-str) """

    # relative data (for sub-linked-strs)
    # Note that the other attributes (e.g. _string) take precedence
    _rel_data: Optional[_RelData[_MetaInfoType]] = None

    _string: Optional[str] = None
    _start_refs: Optional[Sequence[int]] = None
    _end_refs: Optional[Sequence[int]] = None
    _meta_info: _MetaInfoType

    def __init__(self, *,
                 meta_info: _MetaInfoType,
                 string: Optional[str] = None,
                 start_refs: Optional[Sequence[int]] = None,
                 end_refs: Optional[Sequence[int]] = None,
                 rel_data: Optional[_RelData[_MetaInfoType]] = None,
                 ):
        self._meta_info = meta_info
        self._string = string
        self._start_refs = start_refs
        self._end_refs = end_refs
        if string is None or start_refs is None or end_refs is None:
            if rel_data is None:
                raise ValueError('No _RelData provided for incompletely populated instantiation')
            self._rel_data = rel_data

    def get_indices_from_ref_range(self, start_ref, end_ref) -> tuple[int, int]:
        # Note: could also work from rel data
        # Note: this looks easy, but getting it right was surprisingly challenging
        return bisect.bisect(self.get_end_refs(), start_ref), bisect.bisect(self.get_start_refs(), end_ref - 1)

    def with_string(self: LinkedStr_T, string: str) -> LinkedStr_T:
        assert len(string) == len(self)
        return type(self)(meta_info=self._meta_info, string=string, start_refs=self._start_refs,
                          end_refs=self._end_refs, rel_data=self._rel_data)

    def get_start_refs(self) -> Sequence[int]:
        if (sr := self._start_refs) is None:
            rd = self._rel_data
            assert rd is not None
            sr = rd.based_on.get_start_refs()[rd.start_offset:rd.end_offset]
            self._start_refs = sr
        return sr

    def get_end_refs(self) -> Sequence[int]:
        if (er := self._end_refs) is None:
            rd = self._rel_data
            assert rd is not None
            er = rd.based_on.get_end_refs()[rd.start_offset:rd.end_offset]
            self._end_refs = er
        return er

    def get_start_ref(self) -> int:
        # more efficient than calling self.get_start_refs
        if (sr := self._start_refs) is not None:
            return sr[-1]
        rd = self._rel_data
        assert rd is not None
        return rd.based_on.get_start_refs()[rd.start_offset]

    def get_end_ref(self) -> int:
        # more efficient than calling self.get_end_refs
        if (er := self._end_refs) is not None:
            return er[-1]
        rd = self._rel_data
        assert rd is not None
        return rd.based_on.get_end_refs()[rd.end_offset - 1]

    def __len__(self) -> int:
        if (rd := self._rel_data) is not None:
            return rd.end_offset - rd.start_offset
        s = self._string
        assert s is not None
        return len(s)

    def __getitem__(self: LinkedStr_T, item) -> LinkedStr_T:
        if isinstance(item, slice):
            start, stop, step = item.indices(len(self))
            if step == 1:
                return type(self)(meta_info=self._meta_info, rel_data=_RelData(self, start, stop))
            return type(self)(meta_info=self._meta_info, string=str(self)[item], start_refs=self.get_start_refs()[item],
                              end_refs=self.get_end_refs()[item])
        elif isinstance(item, int):
            return type(self)(meta_info=self._meta_info, string=str(self)[item],
                              start_refs=[self.get_start_refs()[item]],
                              end_refs=[self.get_end_refs()[item]])
        elif isinstance(item, re.Match):
            return self[item.start():item.end()]
        else:
            raise TypeError(f'Unsupported type {type(item)}')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(str(self))})'

    def __str__(self) -> str:
        if (s := self._string) is not None:
            return s
        rd = self._rel_data
        assert rd is not None
        self._string = str(rd.based_on)[rd.start_offset:rd.end_offset]
        return self._string

    def strip(self: LinkedStr_T) -> LinkedStr_T:
        str_start = 0
        str_end = 0
        string = str(self)
        for i in range(len(string)):
            if not string[i].isspace():
                str_start = i
                break
        for i in range(len(string) - 1, -1, -1):
            if not string[i].isspace():
                str_end = i + 1
                break
        return self[str_start:str_end]

    def lower(self: LinkedStr_T) -> LinkedStr_T:
        return self.with_string(str(self).lower())

    def upper(self: LinkedStr_T) -> LinkedStr_T:
        return self.with_string(str(self).upper())

    def normalize_spaces(self: LinkedStr_T) -> LinkedStr_T:
        """ replace sequences of whitespaces with a single one."""
        # TODO: clean the code up and potentially optimize it
        new_string = ''
        new_start_refs = []
        new_end_refs = []

        start_refs = self.get_start_refs()
        end_refs = self.get_end_refs()
        string = str(self)
        for i in range(len(self)):
            if not string[i].isspace():
                new_string += string[i]
                new_start_refs.append(start_refs[i])
                new_end_refs.append(end_refs[i])
            else:
                if not (i >= 1 and string[i - 1].isspace()):
                    new_string += ' '
                    new_start_refs.append(start_refs[i])
                    new_end_refs.append(end_refs[i])
        # return self.new(new_string=new_string, new_start_refs=new_start_refs, new_end_refs=new_end_refs)
        return type(self)(meta_info=self._meta_info, string=new_string, start_refs=new_start_refs,
                          end_refs=new_end_refs)

    def get_meta_info(self) -> _MetaInfoType:
        return self._meta_info

    def char_at(self, pos: int) -> str:
        return str(self)[pos]


def string_to_lstr(string: str) -> LinkedStr[None]:
    return LinkedStr(meta_info=None, string=string, start_refs=list(range(len(string))),
                     end_refs=list(range(1, len(string) + 1)))
