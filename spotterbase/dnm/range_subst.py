import itertools
from typing import TypeVar, Generic, Iterable

from spotterbase.dnm.linked_str import LinkedStr_T

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

        ranges: list[tuple[int, int]] = [dnm.get_indices_from_ref_range(s, e) for s, e in self.ordered_ref_ranges]

        new_start_refs: list[int] = []
        new_end_refs: list[int] = []
        strings: list[str] = []

        start_refs = dnm.get_start_refs()
        end_refs = dnm.get_end_refs()

        previous_end: int = 0
        for (from_, to), ref_range in zip(ranges, self.ordered_ref_ranges):
            # TODO: I'm not sure why we need the -1 and +1. We should find out if there is an off-by-one error elsewhere
            # copy until start of range
            new_start_refs.extend(start_refs[previous_end:from_ - 1])
            new_end_refs.extend(end_refs[previous_end:from_ - 1])
            strings.append(str(dnm)[previous_end:from_ - 1])

            # put replacement string
            replacement = self.replacement_values[ref_range]
            new_start_refs.extend(itertools.repeat(ref_range[0], len(replacement)))
            new_end_refs.extend(itertools.repeat(ref_range[1], len(replacement)))
            strings.append(replacement)

            previous_end = to + 1

        new_start_refs.extend(start_refs[previous_end:])
        new_end_refs.extend(end_refs[previous_end:])
        strings.append(str(dnm)[previous_end:])

        return type(dnm)(meta_info=dnm.get_meta_info(), string=''.join(strings), start_refs=new_start_refs,
                         end_refs=new_end_refs)
