from typing import Iterator, List, Optional, Union, Tuple, Set

from lxml.etree import _Element
import re

from spotterbase.dnm.xml_util import get_node_classes


class MatchTree(object):
    def __init__(self, label: str, node: Optional[_Element], children: List['MatchTree']):
        self.label = label
        self.node = node
        self.children = children

    def __getitem__(self, item) -> 'MatchTree':
        if isinstance(item, int):
            return self.children[item]
        elif isinstance(item, str):
            for child in self.children:
                if child.label == item:
                    return child
            raise KeyError(f'No child with label {item}')
        raise Exception(f'Cannot get item {item}')

    @property
    def only_child(self) -> 'MatchTree':
        assert len(self.children) == 1
        return self.children[0]

    def __contains__(self, label: str) -> bool:
        return any(child.label == label for child in self.children)

    def __repr__(self):
        return f'<{self._actual_repr()}>'

    def _actual_repr(self) -> str:
        s = ', '.join(child._actual_repr() for child in self.children)
        if s:
            return f'"{self.label}": <{s}>'
        else:
            return f'"{self.label}"'


class _Match(object):
    def __init__(self, node: Optional[_Element], label: Optional[str] = None, children: Optional[List['_Match']] = None):
        self.node = node
        self.label = label
        self.children: List['_Match'] = children if children is not None else []

    def with_children(self, children: List['_Match']) -> '_Match':
        assert not self.children
        return _Match(self.node, self.label, children)

    def with_label(self, label: str) -> '_Match':
        if self.label is None:
            return _Match(self.node, label, self.children)
        else:
            return _Match(None, label, [self])  # create an "empty" label node

    def to_match_tree(self) -> MatchTree:
        lts = self._to_match_tree()
        if len(lts) != 1:
            return MatchTree('root', self.node, lts)
        else:
            return lts[0]

    def _to_match_tree(self) -> List[MatchTree]:
        child_label_trees = [lt for c in self.children for lt in c._to_match_tree()]
        if self.label is not None:
            return [MatchTree(self.label, self.node, child_label_trees)]
        else:
            return child_label_trees


class Matcher(object):
    def _as_seq_matcher(self) -> 'SeqMatcher':
        raise NotImplemented

    def __add__(self, other: 'Matcher') -> 'SeqMatcher':
        if isinstance(other, MatcherSeqConcat):
            return MatcherSeqConcat([self._as_seq_matcher()] + other.seq_matchers)
        return MatcherSeqConcat([self._as_seq_matcher(), other._as_seq_matcher()])


class SeqMatcher(Matcher):
    def _match(self, nodes: List[_Element]) -> Iterator[Tuple[List[_Match], List[_Element]]]:
        """ Matches some of the `nodes` and yields pairs (`matches`, `rest`),
            where `matches` is the found matches and `rest` are the remaining nodes that still have to be matched. """
        raise NotImplemented

    def _as_seq_matcher(self) -> 'SeqMatcher':
        return self

    def __or__(self, other: Matcher) -> 'SeqMatcher':
        if isinstance(other, MatcherSeqOr):
            return MatcherSeqOr([self] + other.seq_matchers)
        return MatcherSeqOr([self, other._as_seq_matcher()])


class NodeMatcher(Matcher):
    def match(self, node: _Element) -> Iterator[MatchTree]:
        for match in self._match(node):
            yield match.to_match_tree()

    def _match(self, node: _Element) -> Iterator[_Match]:
        raise NotImplemented

    def _as_seq_matcher(self) -> 'SeqMatcher':
        return MatcherNodeAsSeq(self)

    def __pow__(self, label: str) -> 'NodeMatcher':
        """ Add a label the matched note. `**` was chosen due to its precedence """
        return MatcherLabelled(self, label)

    def __truediv__(self, other: Matcher) -> 'NodeMatcher':
        """ `self / other` gives a matcher that matches the children with `other`.
            `/` is left-associative, which is rather counter-intuitive in this case.
            Overriding `__truediv__` in `MatcherNodeWithChildren` mitigates that.
            """
        if isinstance(other, SeqMatcher):
            seq_matcher = other
        elif isinstance(other, NodeMatcher):
            seq_matcher = MatcherSeqAny(other)
        else:
            raise Exception(f'Unsupported object for children: {type(other)}')
        return MatcherNodeWithChildren(self, seq_matcher, allow_remainder=isinstance(other, NodeMatcher))

    def __or__(self, other: 'NodeMatcher') -> 'NodeMatcher':
        assert isinstance(other, NodeMatcher)
        if isinstance(other, MatcherNodeOr):
            return MatcherNodeOr([self] + other.node_matchers)
        return MatcherNodeOr([self, other])

    def with_class(self, *classes: str) -> 'NodeMatcher':
        return MatcherNodeWithClass(self, set(classes))

    def with_text(self, regex: str, require_full_match: bool = True) -> 'NodeMatcher':
        return MatcherNodeWithText(self, re.compile(regex), require_full_match=require_full_match)


class MatcherSeqAny(SeqMatcher):
    """ Matches a whole sequence if a single element matches the specified node matcher """

    def __init__(self, node_matcher: NodeMatcher):
        self.node_matcher = node_matcher

    def _match(self, nodes: List[_Element]) -> Iterator[Tuple[List[_Match], List[_Element]]]:
        for node in nodes:
            for match in self.node_matcher._match(node):
                yield [match], []


class MatcherSeqConcat(SeqMatcher):
    """ Concatenation of sequence matchers """

    def __init__(self, seq_matchers: List[SeqMatcher]):
        self.seq_matchers = seq_matchers

    def _match(self, nodes: List[_Element], matchers: Optional[List[SeqMatcher]] = None) \
            -> Iterator[Tuple[List[_Match], List[_Element]]]:
        if matchers is None:
            matchers = self.seq_matchers
        if not matchers:
            yield [], nodes
        else:
            for match, remainder in matchers[0]._match(nodes):
                if len(matchers) == 1:
                    yield match, remainder
                else:
                    for submatches, lastremainder in self._match(remainder, matchers[1:]):
                        yield match + submatches, lastremainder

    def __add__(self, other: Matcher) -> 'SeqMatcher':
        if isinstance(other, MatcherSeqConcat):
            return MatcherSeqConcat(self.seq_matchers + other.seq_matchers)
        return MatcherSeqConcat(self.seq_matchers + [other._as_seq_matcher()])


class MatcherSeqOr(SeqMatcher):
    def __init__(self, seq_matchers: List[SeqMatcher]):
        self.seq_matchers = seq_matchers

    def _match(self, nodes: List[_Element]) -> Iterator[Tuple[List[_Match], List[_Element]]]:
        for matcher in self.seq_matchers:
            for matches, remainder in matcher._match(nodes):
                yield matches, remainder

    def __or__(self, other: Matcher) -> 'SeqMatcher':
        if isinstance(other, MatcherSeqOr):
            return MatcherSeqOr(self.seq_matchers + other.seq_matchers)
        return MatcherSeqOr(self.seq_matchers + [other._as_seq_matcher()])


class MatcherNodeAsSeq(SeqMatcher):
    def __init__(self, node_matcher: NodeMatcher):
        self.node_matcher = node_matcher

    def _match(self, nodes: List[_Element]) -> Iterator[Tuple[List[_Match], List[_Element]]]:
        if not nodes:
            return iter(())
        for match in self.node_matcher._match(nodes[0]):
            yield [match], nodes[1:]


class MatcherNodeWithClass(NodeMatcher):
    def __init__(self, node_matcher: NodeMatcher, acceptable_classes: Set[str]):
        self.node_matcher = node_matcher
        self.acceptable_classes = acceptable_classes

    def _match(self, node: _Element) -> Iterator[_Match]:
        if any(c in self.acceptable_classes for c in get_node_classes(node)):
            return self.node_matcher._match(node)
        return iter(())


class MatcherNodeWithText(NodeMatcher):
    def __init__(self, node_matcher: NodeMatcher, regex: re.Pattern, require_full_match: bool):
        self.node_matcher = node_matcher
        self.regex = regex
        self.require_full_match = require_full_match

    def _match(self, node: _Element) -> Iterator[_Match]:
        text = node.text if node.text is not None else ''
        if (self.require_full_match and self.regex.fullmatch(text)) or\
                (not self.require_full_match and self.regex.match(text)):
            return self.node_matcher._match(node)
        return iter(())


class MatcherTag(NodeMatcher):
    def __init__(self, tagname: str):
        self.tagname = tagname

    def _match(self, node: _Element) -> Iterator[_Match]:
        if node.tag == self.tagname:
            yield _Match(node)


class MatcherAnyNode(NodeMatcher):
    def _match(self, node: _Element) -> Iterator[_Match]:
        return iter([_Match(node)])


class MatcherNodeOr(NodeMatcher):
    def __init__(self, node_matchers: List[NodeMatcher]):
        self.node_matchers = node_matchers

    def _match(self, node: _Element) -> Iterator[_Match]:
        for matcher in self.node_matchers:
            for match in matcher._match(node):
                yield match

    def __or__(self, other: 'NodeMatcher') -> 'NodeMatcher':
        assert isinstance(other, NodeMatcher)
        if isinstance(other, MatcherNodeOr):
            return MatcherNodeOr(self.node_matchers + other.node_matchers)
        return MatcherNodeOr(self.node_matchers + [other])


class MatcherNodeWithChildren(NodeMatcher):
    def __init__(self, node_matcher: NodeMatcher, seq_matcher: SeqMatcher, allow_remainder: bool = False):
        self.node_matcher = node_matcher
        self.seq_matcher = seq_matcher
        self.allow_remainder = allow_remainder

    def _match(self, node: _Element) -> Iterator[_Match]:
        for match in self.node_matcher._match(node):
            for submatch, remaining in self.seq_matcher._match(node.getchildren()):
                if self.allow_remainder or not remaining:
                    yield match.with_children(submatch)

    def __truediv__(self, other: Matcher) -> 'MatcherNodeWithChildren':
        if isinstance(self.seq_matcher, MatcherSeqAny):
            return MatcherNodeWithChildren(self.node_matcher, MatcherSeqAny(self.seq_matcher.node_matcher / other),
                                           self.allow_remainder)
        else:
            raise Exception(f'Cannot use / in this case (left-hand-side is not a simple path)')


class MatcherLabelled(NodeMatcher):
    def __init__(self, node_matcher: NodeMatcher, label: str):
        self.node_matcher = node_matcher
        self.label = label

    def _match(self, node: _Element) -> Iterator[_Match]:
        for match in self.node_matcher._match(node):
            yield match.with_label(self.label)


# Short hands
any_tag: NodeMatcher = MatcherAnyNode()
empty_seq: SeqMatcher = MatcherSeqConcat([])


def tag(name: str) -> NodeMatcher:
    return MatcherTag(name)


def seq(*matchers: Union[NodeMatcher, SeqMatcher]) -> SeqMatcher:
    return sum(matchers, MatcherSeqConcat([]))  # type: ignore


def maybe(matcher: Union[NodeMatcher, SeqMatcher]) -> SeqMatcher:
    return matcher._as_seq_matcher() | empty_seq
