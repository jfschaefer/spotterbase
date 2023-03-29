import abc
from typing import Iterable, TypeVar, Optional

from lxml.etree import _ElementTree, _Element

from spotterbase.selectors.offset_converter import OffsetConverter, DomOffsetRange
from spotterbase.dnm.dnm import Dnm, DnmStr, DnmRange, DnmPoint, DnmMatchIssues
from spotterbase.selectors.dom_range import DomRange
from spotterbase.dnm.xml_util import XmlNode


class Token(abc.ABC):
    """ A segment of the DOM, corresponding to a segment of the DnmStr. """
    string: str     # string representation of the token
    node: XmlNode  # node that is covered by the token

    def to_range(self, offset: int) -> DomRange:
        """ Returns the DomRange corresponding to self.string[offset] """
        raise NotImplementedError()


class TokenGenerator(abc.ABC):
    def process(self, node: _Element) -> Iterable[Token]:
        raise NotImplementedError()


TokenBasedDnm_T = TypeVar('TokenBasedDnm_T', bound='TokenBasedDnm')


class TokenBasedDnm(Dnm):
    """ An implementation of Dnm using tokens """

    def __init__(self, tree: _ElementTree, tokens: list[Token], offset_converter: Optional[OffsetConverter] = None):
        self.tree = tree
        self.tokens: list[Token] = tokens
        self.offset_converter: Optional[OffsetConverter] = offset_converter

        # BACK REFERENCES (dnm offset -> token)
        self.back_refs: list[tuple[int, int]] = []    # token number, relative offset
        for token_number, token in enumerate(self.tokens):
            for rel_offset in range(len(token.string)):
                self.back_refs.append((token_number, rel_offset))

        self.string = ''.join(token.string for token in self.tokens)

        # FORWARD REFERENCES (node offset (from offset converter) -> dnm offset)
        self.forward_refs: Optional[list[Optional[DomOffsetRange]]] = None

    def _require_offset_converter(self) -> OffsetConverter:
        if self.offset_converter is None:
            # note: usually, an offset converter exists anyway and creating another one is costly.
            # Therefore, it seems better not to silently create one.
            raise Exception('No offset converter was provided to the DNM')
        return self.offset_converter

    @classmethod
    def from_token_generator(cls: type[TokenBasedDnm_T], tree: _ElementTree, generator: TokenGenerator,
                             offset_converter: Optional[OffsetConverter] = None)\
            -> TokenBasedDnm_T:
        tokens = list(generator.process(tree.getroot()))
        return cls(tree, tokens, offset_converter)

    def get_dnm_str(self, dnm_range: Optional[DnmRange] = None) -> DnmStr:
        if dnm_range is not None:
            from_, to = dnm_range.get_offsets()
            return DnmStr(self.string[from_:to + 1], tuple(range(from_, to + 1)), self)
        else:
            return DnmStr(self.string, tuple(range(len(self.string))), self)

    def offset_to_range(self, offset: int) -> DomRange:
        token = self.tokens[self.back_refs[offset][0]]
        rel_offset = self.back_refs[offset][1]
        return token.to_range(rel_offset)

    def dom_range_to_dnm_range(self, dom_range: DomRange | DomOffsetRange) -> tuple[DnmRange, DnmMatchIssues]:
        converter: OffsetConverter = self._require_offset_converter()

        # note: forward_refs are loaded lazily as an optimization
        if self.forward_refs is None:
            self.forward_refs = [None] * len(self.back_refs)

        fwd_refs: list[Optional[DomOffsetRange]] = self.forward_refs

        def get_ref(i) -> DomOffsetRange:
            ref = fwd_refs[i]
            if ref is None:
                ref = converter.convert_dom_range(self.offset_to_range(i))
            fwd_refs[i] = ref
            return ref

        if isinstance(dom_range, DomRange):
            required_range: DomOffsetRange = converter.convert_dom_range(dom_range)
        else:
            required_range = dom_range

        def bisect(goal: int, take_start_val: bool):
            # For the return value r we will have: (values before (<) r) <= goal < (values after (>=) r)
            lower: int = 0
            upper: int = len(fwd_refs)
            # loop invariant: (value at lower-1) <= goal < (value at upper)
            while lower < upper:
                center = (lower + upper) // 2
                value = get_ref(center).start if take_start_val else get_ref(center).end
                if value > goal:
                    upper = center
                else:
                    lower = center + 1
            return lower

        # start at the first forward reference that ends after (>) required_range.start
        start_index = bisect(required_range.start, take_start_val=False)

        # end at the last forward reference that starts before (<) required_range.end
        # equivalently, end at the last forward reference that starts before (<=) required_range.end - 1
        end_index = bisect(required_range.end - 1, take_start_val=True) - 1

        return (
            DnmRange(from_=DnmPoint(start_index, self), to=DnmPoint(end_index, self)),
            DnmMatchIssues(
                dom_start_earlier=required_range.start < get_ref(start_index).start,
                dom_end_later=required_range.end > get_ref(end_index).end,
                dom_start_later=required_range.start > get_ref(start_index).start,
                dom_end_earlier=required_range.end < get_ref(end_index).end
            )
        )
