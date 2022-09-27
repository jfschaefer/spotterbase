
__all__ = ['LStr']

from typing import TypeVar

T = TypeVar('T', bound='LStr')   # TODO: Replace with ``typing.Self'' in Python 3.11


class LStr:
    def __init__(self, string: str, backrefs: list[int]):
        self.string = string
        self.backrefs = backrefs

    def new(self: T, new_string: str, new_backrefs: list[int]) -> T:
        """ Intended to be overwritten in subclasses if more data has to be copied (e.g. a source document) """
        return self.__class__(new_string, new_backrefs)

    def __len__(self) -> int:
        return len(self.string)

    def __getitem__(self: T, item) -> T:
        match item:
            case slice():
                return self.new(self.string[item], self.backrefs[item])
            case int():
                return self.new(self.string[item], [self.backrefs[item]])
            case other:
                raise NotImplementedError(f'Unsupported type {type(other)}')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(self.string)})'

    def __str__(self) -> str:
        return self.string

    def __eq__(self, other) -> bool:
        return self.string == str(other)
