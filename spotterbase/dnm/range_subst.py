import itertools
import warnings
from typing import TypeVar, Generic, Iterable

from spotterbase.dnm.linked_str import LinkedStr_T


warnings.warn('This module is deprecated. '
              'Use the LinkedStr.replacements_at_positions instead.', DeprecationWarning)


_T = TypeVar('_T')


class RangeSubstituter(Generic[_T]):
    substitution_values: dict[tuple[int, int], _T]
    replacement_values: dict[tuple[int, int], str]
    ordered_ref_ranges: list[tuple[int, int]]

    def __init__(self, to_substitute: Iterable[tuple[tuple[int, int], tuple[str, _T]]]):
        """ to_substitute elements should be of the form ((ref_start, ref_end), (replacement_string, value))"""
        s = {}
        v = {}
        for range_, value in to_substitute:
            assert range_ not in s
            s[range_] = value[0]
            v[range_] = value[1]
        self.replacement_values = s
        self.substitution_values = v
        self.ordered_ref_ranges = list(s.keys())
        self.ordered_ref_ranges.sort()
        assert all(x[1] <= y[0] for x, y in itertools.pairwise(self.ordered_ref_ranges)), 'Some ranges are overlapping'

    def apply(self, dnm: LinkedStr_T) -> LinkedStr_T:
        if not self.ordered_ref_ranges:  # nothing to do
            return dnm

        return dnm.replacements_at_positions(
            [(x, y, self.replacement_values[(x, y)]) for x, y in self.ordered_ref_ranges]
        )
