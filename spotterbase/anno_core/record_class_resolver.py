from spotterbase.anno_core.annotation import Annotation
from spotterbase.anno_core.annotation_creator import SpotterRun
from spotterbase.anno_core.tag_body import SimpleTagBody, MultiTagBody, Tag, TagSet
from spotterbase.anno_core.selector import OffsetSelector, PathSelector, ListSelector
from spotterbase.anno_core.target import FragmentTarget
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
