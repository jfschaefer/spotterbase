from __future__ import annotations

import abc
import dataclasses

from spotterbase.rdf.uri import Uri


class PropertyPath(abc.ABC):
    @abc.abstractmethod
    def to_string(self) -> str:
        ...
    
    def inverted(self) -> InvertedPropertyPath:
        return InvertedPropertyPath(self)

    def __truediv__(self, other) -> SequencePropertyPath:
        return SequencePropertyPath([self])/other


@dataclasses.dataclass
class UriPath(PropertyPath):
    uri: Uri

    def to_string(self) -> str:
        return format(self.uri, '<>')


@dataclasses.dataclass
class InvertedPropertyPath(PropertyPath):
    path: PropertyPath

    def to_string(self):
        return f'^{self.path.to_string()}'


@dataclasses.dataclass
class SequencePropertyPath(PropertyPath):
    sequence: list[PropertyPath]

    def __truediv__(self, other) -> PropertyPath:
        if isinstance(other, Uri):
            return SequencePropertyPath(self.sequence + [UriPath(other)])
        elif isinstance(other, SequencePropertyPath):
            return SequencePropertyPath(self.sequence + other.sequence)
        elif isinstance(other, PropertyPath):
            return SequencePropertyPath(self.sequence + [other])
        else:
            raise Exception(f'Unsupported argument type {type(other)}')

    def to_string(self):
        return ' / '.join([el.to_string() for el in self.sequence])