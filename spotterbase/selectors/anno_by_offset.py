from typing import Iterable, Optional

from intervaltree import IntervalTree
from lxml.etree import _Element

from spotterbase.model_core import Annotation
from spotterbase.selectors.offset_converter import DomOffsetRange


class AnnoByOffset:
    def __init__(self, annos: Iterable[tuple[DomOffsetRange, Annotation]] = ()):
        self.it = IntervalTree()
        self._root: Optional[_Element] = None
        for anno in annos:
            self.add_annotation(*anno)

    def add_annotation(self, range_: DomOffsetRange, annotation: Annotation):
        self.it.addi(range_.start, range_.end, annotation)
        if self._root is None:
            self._root = range_.converter.root
        else:
            # technically, it's okay to have them from different DOMs,
            # but that is unlikelye and this way we can catch errors that would otherwise be hard to debug
            assert self._root == range_.converter.root, 'the annotations must be from the same DOM'

    def get_annotations_from_range(self, range_: DomOffsetRange) -> list[Annotation]:
        if self._root is not None:
            assert range_.converter.root == self._root, 'the range must be from the same DOM'
        return [iv.data for iv in self.it[range_.start:range_.end]]

    def get_annotations_from_point(self, point: int) -> list[Annotation]:
        return [iv.data for iv in self.it[point]]

    def __getitem__(self, item):
        if isinstance(item, DomOffsetRange):
            return self.get_annotations_from_range(item)
        elif isinstance(item, int):
            return self.get_annotations_from_point(item)
        else:
            raise ValueError(f'Unsupported item type: {type(item)}')
