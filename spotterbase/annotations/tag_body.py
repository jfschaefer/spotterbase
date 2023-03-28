from __future__ import annotations

from typing import Optional

from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo
from spotterbase.concept_graphs.oa_support import OA_PRED
from spotterbase.concept_graphs.sb_support import SB_PRED
from spotterbase.rdf.literal import Uri
from spotterbase.rdf.vocab import XSD
from spotterbase.sb_vocab import SB


class SimpleTagBody(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.SimpleTagBody,
        attrs=[
            AttrInfo('tag', SB_PRED.val),
        ]
    )

    tag: Uri

    def __init__(self, tag: Optional[Uri] = None):
        self._set_attr_if_not_none('tag', tag)


class MultiTagBody(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.MultiTagBody,
        attrs=[
            AttrInfo('tags', SB_PRED.val, multi_target=True),
        ]
    )

    tags: list[Uri]

    def __init__(self, tags: Optional[list[Uri]] = None):
        self._set_attr_if_not_none('tags', tags)


class Tag(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.Tag,
        attrs=[
            AttrInfo('belongs_to', SB_PRED.belongsTo),
            AttrInfo('label', OA_PRED.label, literal_type=XSD.string),
            AttrInfo('comment', SB_PRED.comment),
        ],
        is_root_concept=True
    )
    label: str
    belongs_to: Uri
    comment: str

    def __init__(self, uri: Optional[Uri] = None, label: Optional[str] = None, belongs_to: Optional[Uri] = None,
                 comment: Optional[str] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('label', label)
        self._set_attr_if_not_none('belongs_to', belongs_to)
        self._set_attr_if_not_none('comment', comment)


class TagSet(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.TagSet,
        attrs=[
            AttrInfo('tags', SB_PRED.belongsTo_Rev, multi_target=True),
            AttrInfo('label', OA_PRED.label, literal_type=XSD.string),
            AttrInfo('comment', SB_PRED.comment),
        ],
        is_root_concept=True
    )

    # tags: list[Uri]
    comment: str
    label: str
    tags: list[Uri]

    def __init__(self, uri: Optional[Uri] = None, label: Optional[str] = None, comment: Optional[str] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('label', label)
        self._set_attr_if_not_none('comment', comment)
