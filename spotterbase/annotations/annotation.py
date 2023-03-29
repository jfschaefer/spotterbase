from __future__ import annotations

from typing import Any, Optional

from spotterbase.records.record import Record, RecordInfo, AttrInfo, FieldUnknownRecord
from spotterbase.records.oa_support import OA_PRED
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import OA


class Annotation(Record):
    record_info = RecordInfo(
        record_type=OA.Annotation,
        attrs=[
            AttrInfo('target_uri', OA_PRED.target),
            AttrInfo('body', OA_PRED.body, field_info=FieldUnknownRecord),
            AttrInfo('creator_uri', OA_PRED.creator),
        ],
        is_root_record=True,
    )

    # attributes
    target_uri: Uri
    body: Any
    creator_uri: Optional[Uri]

    def __init__(self, uri: Optional[Uri] = None, target_uri: Optional[Uri] = None,
                 body: Optional[Any] = None, creator_uri: Optional[Uri] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('target_uri', target_uri)
        self._set_attr_if_not_none('body', body)
        self._set_attr_if_not_none('creator_uri', creator_uri)
