from typing import Optional

from spotterbase.model_core import SB
from spotterbase.model_core.body import TagSet, Tag
from spotterbase.rdf.uri import Uri, Vocabulary, NameSpace
from spotterbase.rdf.vocab import XSD
from spotterbase.records.jsonld_support import JsonLdContext
from spotterbase.records.record import Record, RecordInfo, AttrInfo, PredInfo


class DECL(Vocabulary):
    NS: NameSpace = NameSpace(SB.NS.uri / 'ext/decl/', prefix='decl:')

    Identifier: Uri
    IdentifierOccurrence: Uri
    IdentifierDeclaration: Uri
    IdentifierTypeRestriction: Uri

    occurrenceOf: Uri
    restricts: Uri
    hasPolarity: Uri
    declares: Uri
    idString: Uri


class DECL_PRED:
    occurrenceOf = PredInfo(DECL.occurrenceOf, json_ld_term='decl:occurrenceOf', json_ld_type_is_id=True)
    restricts = PredInfo(DECL.restricts, json_ld_term='decl:restricts', json_ld_type_is_id=True)
    idString = PredInfo(DECL.idString, json_ld_term='decl:idString', literal_type=XSD.string)
    hasPolarity = PredInfo(DECL.hasPolarity, json_ld_term='decl:hasPolarity', json_ld_type_is_id=True)
    declares = PredInfo(DECL.declares, json_ld_term='decl:declares', json_ld_type_is_id=True)


DECL_JSONLD_CTX: JsonLdContext = JsonLdContext(
    uri=None,
    namespaces=[DECL.NS],
    pred_infos=list(p_info for p_info in DECL_PRED.__dict__.values() if isinstance(p_info, PredInfo)),
    terms=[
        ('decl:Identifier', DECL.Identifier),
        ('decl:IdentifierTypeRestriction', DECL.IdentifierTypeRestriction),
        ('decl:IdentifierOccurrence', DECL.IdentifierOccurrence),
        ('decl:IdentifierDeclaration', DECL.IdentifierDeclaration),
    ]
)


class Identifier(Record):
    record_info = RecordInfo(
        record_type=DECL.Identifier,
        attrs=[
            AttrInfo('id_string', DECL_PRED.idString)
        ],
        is_root_record=True,
    )

    id_string: Optional[str] = None

    def __init__(self, uri: Optional[Uri] = None, id_string: Optional[str] = None):
        super().__init__(uri=uri, id_string=id_string)


class IdentifierOccurrence(Record):
    record_info = RecordInfo(
        record_type=DECL.IdentifierOccurrence,
        attrs=[
            AttrInfo('occurrence_of', DECL_PRED.occurrenceOf),
        ],
    )

    occurrence_of: Uri

    def __init__(self, uri: Optional[Uri] = None, occurrence_of: Optional[Uri] = None):
        super().__init__(uri=uri, occurrence_of=occurrence_of)


class IdentifierDeclaration(Record):
    record_info = RecordInfo(
        record_type=DECL.IdentifierDeclaration,
        attrs=[
            AttrInfo('polarity', DECL_PRED.hasPolarity),
            AttrInfo('declares', DECL_PRED.declares),
        ],
    )

    polarity: Uri
    declares: Uri

    def __init__(self, uri: Optional[Uri] = None, declares: Optional[Uri] = None, polarity: Optional[Uri] = None):
        super().__init__(uri=uri, declares=declares, polarity=polarity)


class IdentifierTypeRestriction(Record):
    record_info = RecordInfo(
        record_type=DECL.IdentifierTypeRestriction,
        attrs=[
            AttrInfo('restricts', DECL_PRED.restricts),
        ],
    )

    restricts: Uri

    def __init__(self, uri: Optional[Uri] = None, restricts: Optional[Uri] = None):
        super().__init__(uri=uri, restricts=restricts)


class PolarityVocab(Vocabulary):
    NS: NameSpace = NameSpace(DECL.NS['polarity/'])

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
