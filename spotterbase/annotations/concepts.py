from spotterbase.annotations.annotation import Annotation
from spotterbase.annotations.annotation_creator import SpotterRun
from spotterbase.annotations.tag_body import SimpleTagBody, MultiTagBody, Tag, TagSet
from spotterbase.annotations.selector import OffsetSelector, PathSelector, ListSelector
from spotterbase.annotations.target import FragmentTarget
from spotterbase.concept_graphs.concept_resolver import ConceptResolver

ANNOTATION_CONCEPT_RESOLVER: ConceptResolver = ConceptResolver([
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
