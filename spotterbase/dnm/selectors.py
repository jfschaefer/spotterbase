from __future__ import annotations

import functools
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
            return f'char({dp.node.getroottree().getpath(dp.node)}/text()[1],{dp.text_offset + int(dp.after)})'
        elif dp.tail_offset is not None:
            text_count = 0
            assert (parent := dp.node.getparent()) is not None
            if parent.text:
                text_count += 1
            for child in parent:
                if child.tail:
                    text_count += 1
                if child == dp.node:
                    break
            return f'char({dp.node.getroottree().getpath(parent)}/text()[{text_count}],{dp.tail_offset + int(dp.after)})'
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







class TextOffsetTracker:
    root: _Element
    _node_to_offset: dict[_Element, int]

    @functools.lru_cache(maxsize=10)   # TODO: Is this okay? Theoretically, the DOM could be modified (though for all intended use-cases, we only care about the original one)
    def __new__(cls, root: _Element) -> TextOffsetTracker:
        return super().__new__(cls, root)

    def __init__(self, root: _Element):
        counter = 0
        node_to_offset = {}

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
