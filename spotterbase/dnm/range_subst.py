import itertools
from typing import TypeVar, Generic, Iterable

from spotterbase.dnm.dnm import Dnm, DnmRange

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

    def apply(self, dnm: Dnm) -> Dnm:
        if not self.ordered_ref_ranges:  # nothing to do
            return dnm

        dnm_ranges: list[DnmRange] = [dnm.dnm_range_from_ref_range(s, e)[0] for s, e in self.ordered_ref_ranges]

        new_start_refs: list[int] = []
        new_end_refs: list[int] = []
        strings: list[str] = []

        previous_end: int = 0
        for dnm_range, ref_range in zip(dnm_ranges, self.ordered_ref_ranges):
            # TODO: I'm not sure why we need the -1 and +1. We should find out if there is an off-by-one error elsewhere
            # copy until start of range
            new_start_refs.extend(dnm.start_refs[previous_end:dnm_range.from_ - 1])
            new_end_refs.extend(dnm.end_refs[previous_end:dnm_range.from_ - 1])
            strings.append(dnm.string[previous_end:dnm_range.from_ - 1])

            # put replacement string
            replacement = self.replacement_values[ref_range]
            new_start_refs.extend(itertools.repeat(ref_range[0], len(replacement)))
            new_end_refs.extend(itertools.repeat(ref_range[1], len(replacement)))
            strings.append(replacement)

            previous_end = dnm_range.to + 1

        new_start_refs.extend(dnm.start_refs[previous_end:])
        new_end_refs.extend(dnm.end_refs[previous_end:])
        strings.append(dnm.string[previous_end:])

        return dnm.new(''.join(strings), new_start_refs, new_end_refs)
