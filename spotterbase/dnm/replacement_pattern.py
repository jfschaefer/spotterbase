from __future__ import annotations

import abc
import dataclasses
import functools
from typing import Optional, Callable


class ReplacementPattern(abc.ABC):
    @abc.abstractmethod
    def __call__(self, category: str, number: Optional[int] = None) -> str:
        ...


@functools.lru_cache(maxsize=2**16)    # apparently, caching makes a big difference here
def _hyphenate(category: str) -> str:
    return '-'.join(category.split(' '))


@functools.lru_cache(maxsize=2**16)
def _camel_case(category: str) -> str:
    return ''.join(part.capitalize() for part in category.split(' '))


@functools.lru_cache(maxsize=2**16)
def _all_caps(category: str) -> str:
    return ''.join(part.upper() for part in category.split(' '))


class CategoryStyle:
    HYPHENATED = _hyphenate     # math-equation
    CAMEL_CASE = _camel_case    # MathEquation
    ALL_CAPS = _all_caps        # MATHEQUATION


@dataclasses.dataclass(frozen=True)
class StandardReplacementPattern(ReplacementPattern):
    prefix: str = ''
    infix: str = ''
    suffix: str = ''
    include_infix_if_unnumbered: bool = False
    include_prefix_suffix_if_unnumbered: bool = True
    category_style: Callable[[str], str] = CategoryStyle.CAMEL_CASE

    def __call__(self, category: str, number: Optional[int] = None) -> str:
        return (
            (self.prefix if number is not None or self.include_prefix_suffix_if_unnumbered else '') +
            self.category_style(category) +
            (self.infix if number is not None or self.include_infix_if_unnumbered else '') +
            (str(number) if number is not None else '') +
            (self.suffix if number is not None or self.include_prefix_suffix_if_unnumbered else '')
        )
