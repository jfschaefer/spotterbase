from __future__ import annotations

import functools
import itertools
from typing import Iterable

from lxml.etree import _Element, _Comment

from spotterbase.dnm.dnm import DomRange, DomPoint
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

        if dp.text_offset is not None:
            return f'char({dp.node.getroottree().getpath(dp.node)},{dp.text_offset})'
        elif dp.tail_offset is not None:
            get_offset = TextOffsetTracker.get_offset_with_tracker
            # Note: on optimizing the offset computation:
            # Computing the number of characters inside ``dp.node`` can be expensive.
            # Instead, we could look at the node after dp.node and compute the offset backwards.
            # That's trickier (and therefore error-prone) but could improve the efficiency of certain scenarios
            # significantly (but I expect such scenarios to be rare in practice)
            offset = ((get_offset(dp.node) - get_offset(dp.node.getparent()))   # chars until dp.node
                      + sum(len(t) for t in dp.node.itertext())                 # chars inside dp.node
                      + dp.tail_offset)                                         # chars after dp.node
            return f'char({dp.node.getroottree().getpath(dp.node.getparent())},{offset})'
        else:
            if dp.after:
                return f'after-node({dp.node.getroottree().getpath(dp.node)})'
            else:
                return f'node({dp.node.getroottree().getpath(dp.node)})'

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


class TextOffsetTracker:
    root: _Element
    _node_to_offset: dict[_Element, int]

    # TODO: Is caching okay?
    #  Theoretically, the DOM could be modified (though for all intended use-cases, we only care about the original one)
    @functools.lru_cache(maxsize=10)
    def __new__(cls, root: _Element) -> TextOffsetTracker:
        return super().__new__(cls)

    def __init__(self, root: _Element):
        node_to_offset = {root: 0}
        counter = len(root.text or '')

        # Note on optimization:
        # Recursing through the DOM clearly takes some time.
        # There are some optimization strategies:
        # 1. Do the whole thing in C
        # 2. Don't recurse through the whole DOM.
        # Since I don't want to do 1. until it becomes an actual problem, here are some thoughts on 2.:
        # Using an html tree (`lxml.html.parse`), we get the `.text_content()` method, which is very efficient.
        # For getting a single offset, we could implement something much faster (10x faster, according to my benchmark).
        # However, we usually want to get offsets very often (more than 10x), which means that we have to
        # be smarter for any performance gains. In particular, we would need to store the offsets for some nodes,
        # which we could then use for reference. I could not come up with simple (and efficient) way to do so,
        # without specializing e.g. to the arXMLiv corpus.

        # So - no pre-mature optimization for now. Also note that this preparation is ca. 6 times faster
        # than the original parsing.

        def recurse(node: _Element):
            nonlocal counter
            for childe in node.getchildren():
                node_to_offset[childe] = counter
                if not isinstance(childe, _Comment):
                    counter += len(t) if (t := childe.text) else 0
                    recurse(childe)
                counter += len(t) if (t := childe.tail) else 0

        recurse(root)

        self.root = root
        self._node_to_offset = node_to_offset

    @classmethod
    def get_offset_with_tracker(cls, node: _Element) -> int:
        return TextOffsetTracker(node.getroottree().getroot()).get_offset(node)

    def get_offset(self, node: _Element) -> int:
        if node in self._node_to_offset:
            return self._node_to_offset[node]
        if node.getroottree().getroot() != self.root:
            raise Exception(f'Node does not belong to the tree used by this tracker')
        raise Exception(f'The node could not be found (maybe you added it to the DOM after creating the tracker?)')
