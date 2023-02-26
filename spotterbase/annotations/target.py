from __future__ import annotations

from typing import Optional

from spotterbase.annotations.selector import PathSelector, OffsetSelector
from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo
from spotterbase.concept_graphs.oa_support import OA_PRED
from spotterbase.rdf.uri import Uri
from spotterbase.sb_vocab import SB


class FragmentTarget(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.FragmentTarget,
        attrs=[
            AttrInfo('source', OA_PRED.source),
            AttrInfo('selectors', OA_PRED.selector, can_be_multiple=True,
                     target_type={SB.OffsetSelector, SB.PathSelector}),
        ],
        is_root_concept=True,
    )

    # attributes
    source: Uri
    selectors: list[PathSelector | OffsetSelector]

    def __init__(self, uri: Optional[Uri] = None, source: Optional[Uri] = None,
                 selectors: Optional[list] = None):
        self._set_attr_if_not_none('uri', uri)
        self._set_attr_if_not_none('source', source)
        self._set_attr_if_not_none('selectors', selectors)
