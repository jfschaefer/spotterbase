from __future__ import annotations

import abc
import dataclasses

from spotterbase.rdf.uri import Uri


class PropertyPath(abc.ABC):
    @abc.abstractmethod
    def to_string(self, _put_paren: bool = False) -> str:
        ...

    def inverted(self) -> InvertedPropertyPath:
        return InvertedPropertyPath(self)

    def with_star(self) -> StarPropertyPath:
        return StarPropertyPath(self)

    def __truediv__(self, other) -> SequencePropertyPath:
        return SequencePropertyPath([self]) / other


@dataclasses.dataclass
class UriPath(PropertyPath):
    uri: Uri

    def to_string(self, _put_paren: bool = False) -> str:
        return format(self.uri, '<>')


@dataclasses.dataclass
class InvertedPropertyPath(PropertyPath):
    path: PropertyPath

    def to_string(self, _put_paren: bool = False) -> str:
        return f'^{self.path.to_string(_put_paren=True)}'


@dataclasses.dataclass
class StarPropertyPath(PropertyPath):
    path: PropertyPath

    def to_string(self, _put_paren: bool = False) -> str:
        if _put_paren:
            return f'({self.path.to_string(_put_paren=True)}*)'
        else:
            return f'{self.path.to_string(_put_paren=True)}*'


@dataclasses.dataclass
class SequencePropertyPath(PropertyPath):
    sequence: list[PropertyPath]

    def __truediv__(self, other) -> SequencePropertyPath:
        if isinstance(other, Uri):
            return SequencePropertyPath(self.sequence + [UriPath(other)])
        elif isinstance(other, SequencePropertyPath):
            return SequencePropertyPath(self.sequence + other.sequence)
        elif isinstance(other, PropertyPath):
            return SequencePropertyPath(self.sequence + [other])
        else:
            raise Exception(f'Unsupported argument type {type(other)}')

    def to_string(self, _put_paren: bool = False):
        s = ' / '.join([el.to_string(_put_paren=True) for el in self.sequence])
        if _put_paren:
            return f'({s})'
        else:
            return s
