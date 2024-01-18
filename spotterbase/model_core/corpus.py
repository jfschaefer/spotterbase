from typing import Optional

from spotterbase.model_core import SB
from spotterbase.model_core.oa import OA_PRED
from spotterbase.model_core.sb import SB_PRED
from spotterbase.rdf import Uri, UriLike
from spotterbase.rdf.vocab import XSD
from spotterbase.records.record import Record, RecordInfo, AttrInfo


class DocumentInfo(Record):
    record_info = RecordInfo(
        record_type=SB.Document,
        attrs=[
            AttrInfo('license', SB_PRED.license),
            AttrInfo('belongs_to', SB_PRED.belongsTo),
            AttrInfo('title', SB_PRED.title, literal_type=XSD.string),
            AttrInfo('year', SB_PRED.year),
            AttrInfo('based_on', SB_PRED.isBasedOn),
        ],
        is_root_record=True
    )

    license: Optional[Uri]
    belongs_to: Optional[Uri]
    title: Optional[str]
    year: Optional[int]

    def __init__(self, uri: Optional[UriLike] = None, *, license: Optional[UriLike] = None,
                 belongs_to: Optional[UriLike] = None, title: Optional[str] = None, year: Optional[int] = None,
                 based_on: Optional[UriLike] = None):
        super().__init__(uri=Uri.maybe(uri), license=Uri.maybe(license),
                         belongs_to=Uri.maybe(belongs_to), title=title, year=year,
                         based_on=Uri.maybe(based_on))


class CorpusInfo(Record):
    record_info = RecordInfo(
        record_type=SB.Corpus,
        attrs=[
            AttrInfo('label', OA_PRED.label, literal_type=XSD.string),
            AttrInfo('comment', SB_PRED.comment),
            AttrInfo('based_on', SB_PRED.isBasedOn),
        ],
        is_root_record=True
    )

    label: Optional[str]
    comment: Optional[str]

    def __init__(self, uri: Optional[UriLike] = None, *, label: Optional[str] = None, comment: Optional[str] = None,
                 based_on: Optional[UriLike] = None):
        super().__init__(uri=Uri.maybe(uri), label=label, comment=comment, based_on=Uri.maybe(based_on))
