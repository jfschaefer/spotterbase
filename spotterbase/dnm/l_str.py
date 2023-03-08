import re
from typing import TypeVar, Sequence

__all__ = ['LStr']

T = TypeVar('T', bound='LStr')   # TODO: Replace with ``typing.Self'' in Python 3.11


class LStr:
    def __init__(self, string: str, backrefs: Sequence[int]):
        self.string = string
        self.backrefs = backrefs

    def new(self: T, new_string: str, new_backrefs: Sequence[int]) -> T:
        """ Intended to be overwritten in subclasses if more corpora has to be copied (e.g. a source document) """
        return self.__class__(new_string, new_backrefs)

    def __len__(self) -> int:
        return len(self.string)

    def __getitem__(self: T, item) -> T:
        match item:
            case slice():
                return self.new(self.string[item], self.backrefs[item])
            case int():
                return self.new(self.string[item], [self.backrefs[item]])
            case re.Match():
                s = slice(item.start(), item.end())
                return self.new(self.string[s], self.backrefs[s])
            case other:
                raise NotImplementedError(f'Unsupported type {type(other)}')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.string)})'

    def __str__(self) -> str:
        return self.string

    def __eq__(self, other) -> bool:
        return self.string == str(other)

    def strip(self: T) -> T:
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

    def lower(self: T) -> T:
        return self.new(self.string.lower(), self.backrefs)

    def upper(self: T) -> T:
        return self.new(self.string.upper(), self.backrefs)
