from __future__ import annotations

from typing import TypeVar

IntervalT = TypeVar('IntervalT', bound='Interval')


class Interval:
    __slots__ = ('start', 'end')

    start: int
    end: int   # exclusive

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __contains__(self, item) -> bool:
        if isinstance(item, int):
            return self.start <= item < self.end
        elif isinstance(item, Interval):
            return self.start <= item.start and item.end <= self.end
        else:
            return NotImplemented

    def as_range(self) -> range:
        return range(self.start, self.end)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.start}, {self.end})'

    def overlaps(self, other: 'Interval') -> bool:
        if not isinstance(other, Interval):
            return NotImplemented
        return self.start < other.end and other.start < self.end

    def _return_modified(self: IntervalT, start: int, end: int) -> IntervalT:
        """Override this method if your subclass requires additional arguments."""
        return type(self)(start, end)

    def __or__(self: IntervalT, other) -> IntervalT:
        if not isinstance(other, Interval):
            return NotImplemented
        if self.start <= other.end and other.start <= self.end:
            return self._return_modified(min(self.start, other.start), max(self.end, other.end))
        else:
            raise ValueError(f'Intervals do not overlap: {self} and {other}')
