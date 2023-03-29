from __future__ import annotations

from typing import Optional

from spotterbase.records.record import Record, RecordInfo, AttrInfo
from spotterbase.records.oa_support import OA_PRED
from spotterbase.records.sb_support import SB_PRED
from spotterbase.sb_vocab import SB


class PathSelector(Record):
    record_info = RecordInfo(
        record_type=SB.PathSelector,
        attrs=[
            AttrInfo('start', SB_PRED.startPath),
            AttrInfo('end', SB_PRED.endPath),
            AttrInfo('refinement', OA_PRED.refinedBy),
        ]
    )

    start: str
    end: str
    refinement: Optional[ListSelector] = None

    def __init__(self, start: Optional[str] = None, end: Optional[str] = None,
                 refinement: Optional[ListSelector] = None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if refinement is not None:
            self.refinement = refinement


class OffsetSelector(Record):
    record_info = RecordInfo(
        record_type=SB.OffsetSelector,
        attrs=[
            AttrInfo('start', OA_PRED.start),
            AttrInfo('end', OA_PRED.end),
            AttrInfo('refinement', OA_PRED.refinedBy),
        ]
    )

    start: int
    end: int
    refinement: Optional[ListSelector] = None

    def __init__(self, start: Optional[int] = None, end: Optional[int] = None,
                 refinement: Optional[ListSelector] = None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if refinement is not None:
            self.refinement = refinement


class ListSelector(Record):
    record_info = RecordInfo(
        record_type=SB.ListSelector,
        attrs=[
            AttrInfo('selectors', SB_PRED.vals, multi_field=True)
        ]
    )

    selectors: list[PathSelector | OffsetSelector]

    def __init__(self, selectors: Optional[list[PathSelector | OffsetSelector]] = None):
        if selectors is not None:
            self.selectors = selectors
