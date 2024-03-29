from __future__ import annotations

from typing import Optional

from lxml.etree import _Element


def get_parent_asserted(node: _Element) -> _Element:
    parent = node.getparent()
    assert parent is not None
    return parent


class DomPoint:
    """ References a point in the DOM.

    Attributes:
        node: The referenced node.
        text_offset: if not None, that character in the text content is referred to.
        tail_offset: if not None, that character in the tail content is referred to.
        after: actually, we reference whatever comes after.

    Why do we need `after`?
    To be honest, I keep going back and forth between having it and not having it.
    The background is that ranges are right-exclusive because that is the convention in the Web Annotation standard.
    `after` makes things easier in a way. In particular, it lets us include the end of the DOM.
    It also allows us to have `DomPoint` as a simple datastructure without e.g. complex processing code
    for finding whatever comes after.
    """

    def __init__(self, node: _Element, *, text_offset: Optional[int] = None, tail_offset: Optional[int] = None,
                 after: bool = False):
        # after indicates that it refer actually refers to the location right after what is specified
        assert text_offset is None or tail_offset is None
        self.after = after
        self.node = node
        self.text_offset = text_offset
        self.tail_offset = tail_offset

    def is_element(self) -> bool:
        return self.text_offset is None and self.tail_offset is None

    def get_after(self) -> DomPoint:
        assert not self.after, '`after` already set'
        return DomPoint(self.node, text_offset=self.text_offset, tail_offset=self.tail_offset, after=True)

    def __eq__(self, other):
        """ compares with another DomPoint. Note that the equality is incomplete,
        i.e. we do not have for example DomPoint(x, after=True) == DomPoint(x, tail_offset=0). """
        if not isinstance(other, DomPoint):
            raise NotImplementedError()
        return (self.node == other.node and self.text_offset == other.text_offset and
                self.tail_offset == other.tail_offset)

    def __repr__(self) -> str:
        l = [repr(self.node.getroottree().getpath(self.node))]
        if self.text_offset is not None:
            l.append(f'text={self.text_offset}')
        if self.tail_offset is not None:
            l.append(f'tail={self.tail_offset}')
        if self.after:
            l.append(f'after={self.after}')
        return f'DomPoint({", ".join(l)})'


class DomRange:
    def __init__(self, start: DomPoint | DomRange, end: DomPoint | DomRange):
        if isinstance(start, DomPoint):
            self.start = start
        else:
            self.start = start.start
        if isinstance(end, DomPoint):
            self.end = end
        else:
            self.end = end.end

    def __eq__(self, other):
        if not isinstance(other, DomRange):
            raise NotImplementedError()
        return self.start == other.start and self.end == other.end

    def __repr__(self) -> str:
        return f'DomRange({self.start!r}, {self.end!r})'

    def get_containing_node(self) -> _Element:
        """ Note: This does not cover edge cases yet... """
        from_node = self.start.node
        to_node = self.end.node
        if self.end.tail_offset is not None:
            to_node = get_parent_asserted(to_node)

        from_parents = set()
        n: Optional[_Element] = from_node
        while n is not None:
            from_parents.add(n)
            n = n.getparent()

        n = to_node
        while n not in from_parents:
            n = n.getparent()
            assert n is not None
        return n

    @classmethod
    def from_node(cls, node: _Element) -> DomRange:
        return cls(DomPoint(node), DomPoint(node, after=True))
