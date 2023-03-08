from __future__ import annotations

from typing import Any, Optional

from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo, TargetUnknownConcept
from spotterbase.concept_graphs.oa_support import OA_PRED
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import OA


class Annotation(Concept):
    concept_info = ConceptInfo(
        concept_type=OA.Annotation,
        attrs=[
            AttrInfo('target_uri', OA_PRED.target),
            AttrInfo('body', OA_PRED.body, target_type=TargetUnknownConcept),
            AttrInfo('creator_uri', OA_PRED.creator),
        ],
        is_root_concept=True,
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
