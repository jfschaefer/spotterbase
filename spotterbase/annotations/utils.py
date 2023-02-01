from typing import TypeVar

_T: TypeVar = TypeVar('_T')


def as_list(arg: _T | list[_T]) -> list[_T]:
    """ If the argument is not a list, it returns a list containing the argument """
    if isinstance(arg, list):
        return arg
    return [arg]


def extract_if_singleton(list_: list[_T]) -> _T | list[_T]:
    """ If the argument is a singleton list, it returns its argument,
        otherwise, it returns the entire list """
    if len(list_) == 1:
        return list_[0]
    return list_
