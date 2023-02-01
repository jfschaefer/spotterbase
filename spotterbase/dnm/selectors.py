from __future__ import annotations

import itertools
from typing import Iterable, Optional

from spotterbase.dnm.dnm import DomRange, DomPoint
from spotterbase.dnm.text_offset_tracker import TextOffsetTracker
from spotterbase.rdf.base import Subject, Triple, BlankNode
from spotterbase.rdf.literals import StringLiteral
from spotterbase.rdf.vocab import RDF, OA, DCTERMS
from spotterbase.sb_vocab import SB


class SbPointSelector:
    """ Selector for a node """
    _dom_point: DomPoint

    def __init__(self, dom_point: DomPoint):
        """ Note: The signature might change... """
        self._dom_point = dom_point

    @classmethod
    def from_dom_point(cls, dom_point: DomPoint) -> SbPointSelector:
        return SbPointSelector(dom_point)

    def _to_frag_str(self) -> str:
        dp = self._dom_point
        roottree = dp.node.getroottree()
        assert roottree is not None

        if dp.text_offset is not None:
            return f'char({roottree.getpath(dp.node)},{dp.text_offset})'
        elif dp.tail_offset is not None:
            get_offset = TextOffsetTracker.get_text_offset_with_tracker
            parent = dp.node.getparent()
            assert parent is not None   # can't be because of the tail
            # Note: on optimizing the offset computation:
            # Computing the number of characters inside ``dp.node`` can be expensive.
            # Instead, we could look at the node after dp.node and compute the offset backwards.
            # That's trickier (and therefore error-prone) but could improve the efficiency of certain scenarios
            # significantly (but I expect such scenarios to be rare in practice)
            offset = ((get_offset(dp.node) - get_offset(parent))   # chars until dp.node
                      + sum(len(t) for t in dp.node.itertext())                 # chars inside dp.node
                      + dp.tail_offset)                                         # chars after dp.node
            return f'char({roottree.getpath(parent)},{offset})'
        else:
            if dp.after:
                return f'after-node({roottree.getpath(dp.node)})'
            else:
                return f'node({roottree.getpath(dp.node)})'

    def to_triples(self) -> tuple[Subject, Iterable[Triple]]:
        selector = BlankNode()
        return selector, [
            (selector, RDF.type, OA.FragmentSelector),
            (selector, RDF.value, StringLiteral(self._to_frag_str())),
            (selector, DCTERMS.conformsTo, SB.docFrag),
        ]

    def to_dom_point(self) -> DomPoint:
        return self._dom_point


class SbRangeSelector:
    """ Selector for a range """
    _dom_range: DomRange

    def __init__(self, dom_range: DomRange):
        """ Note: Signature might change """
        self._dom_range = dom_range

    @classmethod
    def from_dom_range(cls, dom_range: DomRange) -> SbRangeSelector:
        return SbRangeSelector(dom_range)

    def to_dom_range(self) -> DomRange:
        return self._dom_range

    def to_triples(self) -> tuple[Subject, Iterable[Triple]]:
        # returns selector and triples
        point_selector = SbPointSelector.from_dom_point
        if point := self._dom_range.as_point():
            return point_selector(point).to_triples()
        else:
            start_selector, start_triples = point_selector(self._dom_range.from_).to_triples()
            end_selector, end_triples = point_selector(self._dom_range.to).to_triples()
            selector = BlankNode()
            other_triples: list[Triple] = [
                (selector, RDF.type, OA.RangeSelector),
                (selector, OA.hasStartSelector, start_selector),
                (selector, OA.hasEndSelector, end_selector)
            ]
            return selector, itertools.chain(other_triples, start_triples, end_triples)


class TextRangeSelector:
    """ Selector for a range using offsets """
    _start: int
    _end: int
    _tracker: TextOffsetTracker

    def __init__(self, start, end, tracker):
        """ Note: Signature might change """
        self._start = start
        self._end = end
        self._tracker = tracker

    @classmethod
    def from_dom_range(self, dom_range: DomRange, tracker: Optional[TextOffsetTracker]) -> TextRangeSelector:
        tracker = tracker or TextOffsetTracker(dom_range.from_.node.getroottree().getroot())
        start_point = dom_range.from_
        end_point = dom_range.to
        start_offset: int
        end_offset: int

        # TODO: The following code is somewhat hacky and contains errors (in particular if Comment nodes are present)
        # The SbPointSelector has a comment on improving the efficiency.
        # That might be a good idea here as well and should be implemented along with rigorous unit tests.

        if start_point.text_offset is not None:
            start_offset = tracker.get_node_text_offset(start_point.node) + start_point.text_offset
        elif end_point.tail_offset is not None:
            start_offset = (tracker.get_node_text_offset(start_point.node) +
                            sum(len(t) for t in start_point.node.itertext()) +
                            sum(1 for _ in start_point.node.iterdescendants()) +
                            start_point.tail_offset)
        else:
            start_offset = tracker.get_node_text_offset(end_point.node)

        if end_point.text_offset is not None:
            end_offset = tracker.get_node_text_offset(end_point.node) + end_point.text_offset + 1
        elif end_point.tail_offset is not None:
            end_offset = (tracker.get_node_text_offset(end_point.node) +
                          sum(len(t) for t in end_point.node.itertext()) +
                          sum(1 for _ in end_point.node.iterdescendants()) +
                          end_point.tail_offset + 1)
        else:
            end_offset = (tracker.get_node_text_offset(end_point.node) +
                          sum(len(t) for t in end_point.node.itertext()) +
                          sum(1 for _ in end_point.node.iterdescendants()) +
                          end_point.tail_offset + 1)

        return TextRangeSelector(start_offset, end_offset, tracker)

#     def to_dom_range(self) -> DomRange:
#         return self._dom_range

#    def to_triples(self) -> tuple[Subject, Iterable[Triple]]:
#        # returns selector and triples
