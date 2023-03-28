from typing import Optional

from spotterbase.annotations.tag_body import TagSet, Tag
from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo
from spotterbase.rdf.uri import Uri, Vocabulary, NameSpace
from spotterbase.special_concepts.sbx import SBX, SBX_PRED


class Identifier(Concept):
    concept_info = ConceptInfo(
        concept_type=SBX.Identifier,
        attrs=[
        ],
        is_root_concept=True,
    )

    def __init__(self, uri: Optional[Uri] = None):
        self._set_attr_if_not_none('uri', uri)


class IdentifierOccurrence(Concept):
    concept_info = ConceptInfo(
        concept_type=SBX.IdentifierOccurrence,
        attrs=[
            AttrInfo('occurrence_of', SBX_PRED.occurrenceOf),
        ],
    )

    occurrence_of: Uri

    def __init__(self, uri: Optional[Uri] = None, occurrence_of: Optional[Uri] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('occurrence_of', occurrence_of)


class IdentifierDeclaration(Concept):
    concept_info = ConceptInfo(
        concept_type=SBX.IdentifierDeclaration,
        attrs=[
            AttrInfo('polarity', SBX_PRED.hasPolarity),
            AttrInfo('declares', SBX_PRED.declares),
        ],
    )

    polarity: Uri
    declares: Uri

    def __init__(self, uri: Optional[Uri] = None, declares: Optional[Uri] = None, polarity: Optional[Uri] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('declares', declares)
        self._set_attr_if_not_none('polarity', polarity)


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