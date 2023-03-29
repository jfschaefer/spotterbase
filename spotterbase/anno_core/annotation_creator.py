import datetime
from typing import Optional

from spotterbase.records.record import Record, RecordInfo, AttrInfo
from spotterbase.records.oa_support import OA_PRED
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import XSD
from spotterbase.anno_core.sb import SB, SB_PRED


class SpotterRun(Record):
    record_info = RecordInfo(
        record_type=SB.SpotterRun,
        attrs=[
            AttrInfo('spotter_uri', pred_info=SB_PRED.withSpotter),
            AttrInfo('spotter_version', pred_info=SB_PRED.spotterVersion),
            AttrInfo('label', OA_PRED.label, literal_type=XSD.string),
            AttrInfo('comment', SB_PRED.comment),
            AttrInfo('date', OA_PRED.created),
            # TODO: date
        ]
    )

    spotter_uri: Optional[Uri]
    spotter_version: Optional[str]
    date: Optional[datetime.datetime]
    comment: Optional[str] = None
    label: Optional[str] = None

    def __init__(self,
                 uri: Optional[Uri] = None,
                 spotter_uri: Optional[Uri] = None,
                 spotter_version: Optional[str] = None,
                 date: Optional[datetime.datetime] = None,
                 comment: Optional[str] = None,
                 label: Optional[str] = None):
        super().__init__(
            uri=uri, spotter_uri=spotter_uri, spotter_version=spotter_version, date=date, comment=comment, label=label
        )
