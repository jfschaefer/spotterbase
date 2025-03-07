from __future__ import annotations

import dataclasses
import functools
from typing import Iterable

from intervaltree import IntervalTree, Interval
from lxml.etree import _Element, _Comment

from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.dnm import Dnm
from spotterbase.dnm.node_based_dnm_factory import NodeBasedDnmFactory, SourceHtmlNP
from spotterbase.evaluate.annocollection import AnnoWithFragTarget, AnnoCollection
from spotterbase.rdf import Uri
from spotterbase.selectors.offset_converter import DomOffsetRange


@dataclasses.dataclass
class OffsetEquiConfig:
    """
    ``invisible_nodes``:
        nodes that can be completely ignored (i.e. it doesn't make a difference if they are included or not).
    ``visible_tags``:
        by default, tags are invisible. So if you have ``ab<span>def</span>gh``, it does not make a difference
        if you annotate ``<span>def</span>`` or just ``def`` or just ``<span>def``.
        By adding ``span`` to ``visible_tags``, you can make the span visible.
        This is relevant for meaning-carrying tags (e.g. ``<msqrt>`` in MathML).

    Clarification:
        `'x' in invisible_nodes` is stronger than `'x' not in visible_tags`, because
        it means that the content of `x` is completely irrelevant, while the content
        of a tag not in `visible_tags` is still relevant, just whether the "open" and "close" tags
        are included is irrelevant.

    Note: This is a prototype implementation. In the future, we need support more complex cases
        (e.g. tags that are only visible if they contain certain attributes).
    """
    invisible_nodes: set[str]
    visible_tags: set[str]


class OffsetEquis:
    """Essentially an equivalence relation on offsets"""

    def __init__(self, invis_ranges: Iterable[tuple[int, int]], doc: Document):
        self.invis = IntervalTree(Interval(*r) for r in invis_ranges)
        self.invis.merge_overlaps(strict=False)
        self.doc = doc

    @classmethod
    def from_doc_simple(cls, doc: Document, offset_equi_config: OffsetEquiConfig) -> OffsetEquis:
        oc = doc.get_offset_converter()

        def get_invis_ranges(root: _Element) -> Iterable[tuple[int, int]]:
            for node in root:
                if isinstance(node, _Comment):
                    continue
                if node.tag in offset_equi_config.invisible_nodes:
                    od = oc.get_offset_data(node)
                    yield od.node_text_offset_before, od.node_text_offset_after
                elif node.tag in offset_equi_config.visible_tags:
                    yield from get_invis_ranges(node)
                else:
                    od = oc.get_offset_data(node)
                    yield od.node_text_offset_before, od.node_text_offset_before + 1
                    yield from get_invis_ranges(node)
                    yield od.node_text_offset_after - 1, od.node_text_offset_after

        return OffsetEquis(get_invis_ranges(doc.get_html_tree(cached=True).getroot()), doc)

    def minimize_range(self, dor: DomOffsetRange) -> DomOffsetRange:
        """Returns the shortest range that is equivalent to the input range"""
        start_intervals = self.invis[dor.start]
        assert len(start_intervals) <= 1
        end_intervals = self.invis[dor.end]
        assert len(end_intervals) <= 1

        return DomOffsetRange(
            start=start_intervals.pop().end if start_intervals else dor.start,
            end=end_intervals.pop().begin if end_intervals else dor.end,
            converter=dor.converter)


@dataclasses.dataclass(frozen=True)
class AnnoWithFragTargetPair:
    golden: AnnoWithFragTarget
    prediction: AnnoWithFragTarget

    def get_doc_uri(self) -> Uri:
        assert self.golden.target.source == self.prediction.target.source
        return self.golden.target.source


@dataclasses.dataclass(frozen=True)
class RangeMatching:
    precise_matches: list[AnnoWithFragTargetPair]
    overlaps: list[AnnoWithFragTargetPair]
    golden_only: list[AnnoWithFragTarget]
    prediction_only: list[AnnoWithFragTarget]

    golden_in_multimatches: list[AnnoWithFragTarget]
    prediction_in_multimatches: list[AnnoWithFragTarget]
    multimatches: list[AnnoWithFragTargetPair]

    @classmethod
    def from_anno_collections(
            cls, golden: AnnoCollection, prediction: AnnoCollection, offset_equi_config: OffsetEquiConfig
    ) -> RangeMatching:
        doc_uris = set(golden.fragment_annos_by_source.keys()) | set(prediction.fragment_annos_by_source.keys())

        result = RangeMatching([], [], [], [], [], [], [])

        for doc_uri in doc_uris:
            doc = Resolver.get_document(doc_uri)
            if doc is None:
                raise Exception(f'Document {doc_uri} not found')
            offset_equi = OffsetEquis.from_doc_simple(doc, offset_equi_config)

            def anno_to_interval(anno: AnnoWithFragTarget) -> Interval:
                dom_range = doc.get_selector_converter().target_to_dom(anno.target)[0]
                offset_range = doc.get_offset_converter().convert_dom_range(dom_range)
                minimized_offset_range = offset_equi.minimize_range(offset_range)
                return Interval(minimized_offset_range.start, minimized_offset_range.end, anno)

            golden_intervals = IntervalTree([
                anno_to_interval(anno)
                for anno in golden.fragment_annos_by_source.get(doc_uri, [])
            ])

            golden_to_prediction: dict[AnnoWithFragTarget, list[Interval[AnnoWithFragTarget]]] = {
                i.data: [] for i in golden_intervals
            }
            prediction_to_golden: dict[AnnoWithFragTarget, list[Interval[AnnoWithFragTarget]]] = {}

            for p_anno in prediction.fragment_annos_by_source.get(doc_uri, []):
                prediction_to_golden[p_anno] = []
                interval = anno_to_interval(p_anno)
                for golden_interval in golden_intervals[interval.begin:interval.end]:
                    golden_to_prediction[golden_interval.data].append(interval)
                    prediction_to_golden[p_anno].append(golden_interval)

            for golden_interval in golden_intervals.all_intervals:
                if not golden_to_prediction[golden_interval.data]:
                    result.golden_only.append(golden_interval.data)
                elif len(golden_to_prediction[golden_interval.data]) == 1:
                    prediction_interval = golden_to_prediction[golden_interval.data][0]
                    if prediction_interval.begin == golden_interval.begin and \
                            prediction_interval.end == golden_interval.end:
                        result.precise_matches.append(
                            AnnoWithFragTargetPair(golden_interval.data, prediction_interval.data)
                        )
                    else:
                        result.overlaps.append(AnnoWithFragTargetPair(golden_interval.data, prediction_interval.data))
                else:
                    result.golden_in_multimatches.append(golden_interval.data)
                    for prediction_interval in golden_to_prediction[golden_interval.data]:
                        result.multimatches.append(
                            AnnoWithFragTargetPair(golden=golden_interval.data, prediction=prediction_interval.data)
                        )
            for prediction_interval in prediction_to_golden:
                if not prediction_to_golden[prediction_interval]:
                    result.prediction_only.append(prediction_interval)
                elif len(prediction_to_golden[prediction_interval]) > 1:
                    result.prediction_in_multimatches.append(prediction_interval)

        return result

    def print_overlap_details(self):
        """Prints overlapping annotations in detail to help find out why they only overlap instead of being equal"""

        overlaps = self.overlaps[:]
        overlaps.sort(key=lambda pair: str(pair.get_doc_uri()))

        dnm_factory = NodeBasedDnmFactory(SourceHtmlNP())

        @functools.lru_cache(1)
        def get_doc_and_dnm(uri: Uri) -> tuple[Document, Dnm]:
            doc = Resolver.get_document(uri)
            if doc is None:
                raise Exception(f'Document {uri} not found')
            return doc, dnm_factory.dnm_from_document(doc)

        for pair in self.overlaps:
            doc, dnm = get_doc_and_dnm(pair.get_doc_uri())
            print(f'Golden: {pair.golden.anno.uri}')
            print(repr(str(dnm.sub_dnm_from_dom_range(doc.to_dom(pair.golden.target)[0])[0])))
            print([(s.start, s.end) for s in pair.golden.target.selectors])
            print(f'Prediction: {pair.prediction.anno.uri}')
            print(repr(str(dnm.sub_dnm_from_dom_range(doc.to_dom(pair.prediction.target)[0])[0])))
            print([(s.start, s.end) for s in pair.prediction.target.selectors])
            print()
