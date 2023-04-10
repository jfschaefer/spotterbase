from typing import Optional

from spotterbase.model_core.tag_body import TagSet, Tag
from spotterbase.model_extra.sbx import SBX, SBX_PRED
from spotterbase.rdf.uri import Uri, Vocabulary, NameSpace
from spotterbase.records.record import Record, RecordInfo, AttrInfo


class Identifier(Record):
    record_info = RecordInfo(
        record_type=SBX.Identifier,
        attrs=[
            AttrInfo('id_string', SBX_PRED.idString)
        ],
        is_root_record=True,
    )

    id_string: Optional[str] = None

    def __init__(self, uri: Optional[Uri] = None, id_string: Optional[str] = None):
        super().__init__(uri=uri, id_string=id_string)


class IdentifierOccurrence(Record):
    record_info = RecordInfo(
        record_type=SBX.IdentifierOccurrence,
        attrs=[
            AttrInfo('occurrence_of', SBX_PRED.occurrenceOf),
        ],
    )

    occurrence_of: Uri

    def __init__(self, uri: Optional[Uri] = None, occurrence_of: Optional[Uri] = None):
        super().__init__(uri=uri, occurrence_of=occurrence_of)


class IdentifierDeclaration(Record):
    record_info = RecordInfo(
        record_type=SBX.IdentifierDeclaration,
        attrs=[
            AttrInfo('polarity', SBX_PRED.hasPolarity),
            AttrInfo('declares', SBX_PRED.declares),
        ],
    )

    polarity: Uri
    declares: Uri

    def __init__(self, uri: Optional[Uri] = None, declares: Optional[Uri] = None, polarity: Optional[Uri] = None):
        super().__init__(uri=uri, declares=declares, polarity=polarity)


class IdentifierTypeRestriction(Record):
    record_info = RecordInfo(
        record_type=SBX.IdentifierTypeRestriction,
        attrs=[
            AttrInfo('restricts', SBX_PRED.restricts),
        ],
    )

    restricts: Uri

    def __init__(self, uri: Optional[Uri] = None, restricts: Optional[Uri] = None):
        super().__init__(uri=uri, restricts=restricts)


class PolarityVocab(Vocabulary):
    NS: NameSpace = NameSpace(SBX.NS['polarity/'])

    universal: Uri
    existential: Uri


POLARITY_TAG_SET: TagSet = TagSet(uri=PolarityVocab.NS.uri, label='Polarity of Declaration TagSet',
                                  comment='A declared identifier usually has something we call a "polarity" '
                                          '(for lack of a better word), indicating whether it is quantified '
                                          'existentially or universally (or occasionally something else).')

POLARITY_TAGS: list[Tag] = [
    Tag(uri=PolarityVocab.universal, label='universal', belongs_to=POLARITY_TAG_SET.uri,
        comment='the identifier is universally quantified'),
    Tag(uri=PolarityVocab.existential, label='existential', belongs_to=POLARITY_TAG_SET.uri,
        comment='the identifier is existentially quantified'),
]
