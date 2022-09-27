import abc
from typing import Iterable, TypeVar

from lxml.etree import _ElementTree, _Element

from spotterbase.dnm.dnm import Dnm, DomPoint, DnmStr
from spotterbase.dnm.xml_util import XmlNode


class Token(abc.ABC):
    """ A segment of the DOM, corresponding to a segment of the DnmStr. """
    string: str     # string representation of the token
    node: XmlNode  # node that is covered by the token

    def to_point(self, offset: int) -> DomPoint:
        """ Returns the DomPoint corresponding to self.string[offset] """
        raise NotImplementedError()


class TokenGenerator(abc.ABC):
    def process(self, node: _Element) -> Iterable[Token]:
        raise NotImplementedError()


TokenBasedDnm_T = TypeVar('TokenBasedDnm_T', bound='TokenBasedDnm')


class TokenBasedDnm(Dnm):
    """ An implementation of Dnm using tokens """

    def __init__(self, tree: _ElementTree, tokens: list[Token]):
        self.tree = tree

        self.tokens: list[Token] = tokens

        # BACK REFERENCES
        self.back_refs: list[tuple[int, int]] = []    # token number, relative offset
        for token_number, token in enumerate(self.tokens):
            for rel_offset in range(len(token.string)):
                self.back_refs.append((token_number, rel_offset))

        self.string = ''.join(token.string for token in self.tokens)

    @classmethod
    def from_token_generator(cls: type[TokenBasedDnm_T], tree: _ElementTree, generator: TokenGenerator) -> TokenBasedDnm_T:
        tokens = list(generator.process(tree.getroot()))
        return cls(tree, tokens)

    def get_dnm_str(self) -> DnmStr:
        return DnmStr(self.string, list(range(len(self.string))), self)

    def offset_to_point(self, offset: int) -> DomPoint:
        token = self.tokens[self.back_refs[offset][0]]
        rel_offset = self.back_refs[offset][1]
        return token.to_point(rel_offset)

