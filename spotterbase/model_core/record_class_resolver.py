from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.annotation_creator import SpotterRun
from spotterbase.model_core.body import SimpleTagBody, MultiTagBody, Tag, TagSet
from spotterbase.model_core.selector import OffsetSelector, PathSelector, ListSelector
from spotterbase.model_core.target import FragmentTarget
from spotterbase.records.record_class_resolver import RecordClassResolver

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
