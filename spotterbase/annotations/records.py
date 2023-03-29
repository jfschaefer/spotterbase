from spotterbase.annotations.annotation import Annotation
from spotterbase.annotations.annotation_creator import SpotterRun
from spotterbase.annotations.tag_body import SimpleTagBody, MultiTagBody, Tag, TagSet
from spotterbase.annotations.selector import OffsetSelector, PathSelector, ListSelector
from spotterbase.annotations.target import FragmentTarget
from spotterbase.records.record_class_resolver import RecordClassResolver

ANNOTATION_RECORD_RESOLVER: RecordClassResolver = RecordClassResolver([
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
