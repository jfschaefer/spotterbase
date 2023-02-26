import datetime
from typing import Optional

from spotterbase.concept_graphs.concept_graph import Concept, ConceptInfo, AttrInfo
from spotterbase.concept_graphs.sb_support import SB_PRED
from spotterbase.rdf.uri import Uri
from spotterbase.sb_vocab import SB


class SpotterRun(Concept):
    concept_info = ConceptInfo(
        concept_type=SB.SpotterRun,
        attrs=[
            AttrInfo('spotter_uri', pred_info=SB_PRED.withSpotter),
            AttrInfo('spotter_version', pred_info=SB_PRED.spotterVersion),
            # TODO: date
        ]
    )

    spotter_uri: Optional[Uri]
    spotter_version: Optional[str]
    date: Optional[datetime.datetime]

    def __init__(self,
                 uri: Optional[Uri] = None,
                 spotter_uri: Optional[Uri] = None,
                 spotter_version: Optional[str] = None,
                 date: Optional[datetime.datetime] = None):
        if uri is not None:
            self.uri = uri
        if spotter_uri is not None:
            self.spotter_uri = spotter_uri
        if spotter_version is not None:
            self.spotter_version = spotter_version
        if date is not None:
            self.date = date
