from __future__ import annotations

from typing import Any, Optional

from spotterbase.records.record import Record, RecordInfo, AttrInfo, FieldUnknownRecord
from spotterbase.model_core.oa import OA_PRED, OA
from spotterbase.rdf.uri import Uri, UriLike


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

    def __init__(self, uri: Optional[UriLike] = None, *, target_uri: Optional[UriLike] = None,
                 body: Optional[Any] = None, creator_uri: Optional[Uri] = None):
        super().__init__(uri=Uri.maybe(uri), target_uri=Uri.maybe(target_uri), body=body, creator_uri=creator_uri)
