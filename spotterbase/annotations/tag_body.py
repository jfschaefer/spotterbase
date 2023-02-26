from __future__ import annotations

from typing import Optional

from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo
from spotterbase.concept_graphs.sb_support import SB_PRED
from spotterbase.rdf.base import Uri
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
            AttrInfo('tags', SB_PRED.val, can_be_multiple=True),
        ]
    )

    tags: list[Uri]

    def __init__(self, tags: Optional[list[Uri]] = None):
        self._set_attr_if_not_none('tags', tags)


class Tag(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.Tag,
        attrs=[
            AttrInfo('belongs_to', SB_PRED.belongsTo)
        ],
        is_root_concept=True
    )

    def __init__(self, uri: Optional[Uri] = None, belongs_to: Optional[Uri] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('belongs_to', belongs_to)


class TagSet(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.TagSet,
        attrs=[
            AttrInfo('tags', SB_PRED.contains, can_be_multiple=True)
        ],
        is_root_concept=True
    )

    def __init__(self, uri: Optional[Uri] = None):
        self._set_attr_if_not_none('uri', uri)
