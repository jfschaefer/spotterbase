from __future__ import annotations

from typing import Optional

from spotterbase.model_core.oa import OA_PRED
from spotterbase.model_core.sb import SB, SB_PRED
from spotterbase.rdf.literal import Uri, HtmlFragment
from spotterbase.rdf.vocab import XSD, RDF
from spotterbase.records.record import Record, RecordInfo, AttrInfo


class SimpleTagBody(Record):
    record_info = RecordInfo(
        record_type=SB.SimpleTagBody,
        attrs=[
            AttrInfo('tag', SB_PRED.val),
        ]
    )

    tag: Uri

    def __init__(self, tag: Optional[Uri] = None):
        super().__init__(tag=tag)


class MultiTagBody(Record):
    record_info = RecordInfo(
        record_type=SB.MultiTagBody,
        attrs=[
            AttrInfo('tags', SB_PRED.val, multi_field=True),
        ]
    )

    tags: list[Uri]

    def __init__(self, tags: Optional[list[Uri]] = None):
        super().__init__(tags=tags)


class Tag(Record):
    record_info = RecordInfo(
        record_type=SB.Tag,
        attrs=[
            AttrInfo('belongs_to', SB_PRED.belongsTo),
            AttrInfo('label', OA_PRED.label, literal_type=XSD.string),
            AttrInfo('comment', SB_PRED.comment),
        ],
        is_root_record=True
    )
    label: Optional[str] = None
    belongs_to: Optional[Uri] = None
    comment: Optional[str] = None

    def __init__(self, uri: Optional[Uri] = None, label: Optional[str] = None, belongs_to: Optional[Uri] = None,
                 comment: Optional[str] = None):
        super().__init__(uri=uri, label=label, belongs_to=belongs_to, comment=comment)


class TagSet(Record):
    record_info = RecordInfo(
        record_type=SB.TagSet,
        attrs=[
            AttrInfo('tags', SB_PRED.belongsTo_Rev, multi_field=True),
            AttrInfo('label', OA_PRED.label, literal_type=XSD.string),
            AttrInfo('comment', SB_PRED.comment),
        ],
        is_root_record=True
    )

    # tags: list[Uri]
    comment: Optional[str] = None
    label: Optional[str] = None
    tags: Optional[list[Uri]] = None

    def __init__(self, uri: Optional[Uri] = None, label: Optional[str] = None, comment: Optional[str] = None):
        super().__init__(uri=uri, label=label, comment=comment)


class ReplacedHtmlBody(Record):
    record_info = RecordInfo(
        record_type=SB.ReplacedHtmlBody,
        attrs=[
            AttrInfo('html_frag', SB_PRED.html_val, literal_type=RDF.HTML),
        ]
    )

    html_frag: HtmlFragment

    def __init__(self, html_frag: Optional[HtmlFragment] = None):
        super().__init__(html_frag=html_frag)
