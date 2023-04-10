import re
from typing import TypeVar, Sequence

LinkedStr_T = TypeVar('LinkedStr_T', bound='LinkedStr')


class LinkedStr:
    __slots__ = ('string', 'start_refs', 'end_refs')
    """ Should be treated as immutable! For optimization, back_refs can be copied by reference. """
    def __init__(self, string: str, start_refs: Sequence[int], end_refs: Sequence[int]):
        self.string = string
        self.start_refs = start_refs
        self.end_refs = end_refs

    def get_start_ref(self) -> int:
        return self.start_refs[0]

    def get_end_ref(self) -> int:
        return self.end_refs[-1]

    def new(self: LinkedStr_T, new_string: str, new_start_refs: Sequence[int], new_end_refs) -> LinkedStr_T:
        """ Intended to be overwritten in subclasses if more corpora has to be copied (e.g. a source document) """
        return self.__class__(new_string, new_start_refs, new_end_refs)

    def __len__(self) -> int:
        return len(self.string)

    def __getitem__(self: LinkedStr_T, item) -> LinkedStr_T:
        match item:
            case slice():
                return self.new(self.string[item], self.start_refs[item], self.end_refs[item])
            case int():
                return self.new(self.string[item], [self.start_refs[item]], [self.end_refs[item]])
            case re.Match():
                s = slice(item.start(), item.end())
                return self.new(self.string[s], self.end_refs[s], self.start_refs[s])
            case other:
                raise NotImplementedError(f'Unsupported type {type(other)}')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.string)})'

    def __str__(self) -> str:
        return self.string

    def __eq__(self, other) -> bool:
        return self.string == str(other)

    def strip(self: LinkedStr_T) -> LinkedStr_T:
        str_start = 0
        str_end = 0
        for i in range(len(self.string)):
            if not self.string[i].isspace():
                str_start = i
                break
        for i in range(len(self.string) - 1, -1, -1):
            if not self.string[i].isspace():
                str_end = i + 1
                break
        return self[str_start:str_end]

    def lower(self: LinkedStr_T) -> LinkedStr_T:
        return self.new(self.string.lower(), self.end_refs, self.start_refs)

    def upper(self: LinkedStr_T) -> LinkedStr_T:
        return self.new(self.string.upper(), self.end_refs, self.start_refs)

    def normalize_spaces(self: LinkedStr_T) -> LinkedStr_T:
        """ replace sequences of whitespaces with a single one."""
        # TODO: clean the code up and potentially optimize it
        new_string = ''
        new_start_refs = []
        new_end_refs = []
        for i in range(len(self)):
            if not self.string[i].isspace():
                new_string += self.string[i]
                new_start_refs.append(self.start_refs[i])
                new_end_refs.append(self.end_refs[i])
            else:
                if not (i >= 1 and self.string[i - 1].isspace()):
                    new_string += ' '
                    new_start_refs.append(self.start_refs[i])
                    new_end_refs.append(self.end_refs[i])
        return self.new(new_string=new_string, new_start_refs=new_start_refs, new_end_refs=new_end_refs)


def string_to_lstr(string: str) -> LinkedStr:
    return LinkedStr(string, list(range(len(string))), list(range(1, len(string) + 1)))
