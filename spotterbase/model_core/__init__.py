from spotterbase.model_core.oa import OA, OA_JSONLD_CONTEXT
from spotterbase.model_core.sb import SB_JSONLD_CONTEXT, SB
from spotterbase.rdf import StandardNameSpaces
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.annotation_creator import SpotterRun
from spotterbase.model_core.body import SimpleTagBody, MultiTagBody, Tag, TagSet
from spotterbase.model_core.selector import OffsetSelector, PathSelector, ListSelector
from spotterbase.model_core.target import FragmentTarget, populate_standard_selectors
from spotterbase.records.jsonld_support import DefaultContexts
from spotterbase.records.record_class_resolver import RecordClassResolver, DefaultRecordClassResolver
from spotterbase.records.sparql_populate import DefaultSpecialPopulators

ANNOTATION_RECORD_CLASS_RESOLVER: RecordClassResolver = RecordClassResolver([
    Annotation,
    FragmentTarget,
    OffsetSelector,
    PathSelector,
    ListSelector,
    SimpleTagBody,
    MultiTagBody,
    Tag,
    TagSet,
    SpotterRun,
])


def load():
    StandardNameSpaces.add_namespace(OA.NS)
    StandardNameSpaces.add_namespace(SB.NS)

    for record_type in ANNOTATION_RECORD_CLASS_RESOLVER.record_class_iter():
        DefaultRecordClassResolver.add(record_type)

    DefaultContexts.append(SB_JSONLD_CONTEXT)
    DefaultContexts.append(OA_JSONLD_CONTEXT)

    assert FragmentTarget not in DefaultSpecialPopulators
    DefaultSpecialPopulators[FragmentTarget] = [populate_standard_selectors]
