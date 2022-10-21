from __future__ import annotations

import functools

from lxml.etree import _Element, _Comment


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
            for child in node.iterchildren():
                node_to_offset[child] = counter
                if not isinstance(child, _Comment):
                    counter += len(t) if (t := child.text) else 0
                    recurse(child)
                counter += len(t) if (t := child.tail) else 0

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
