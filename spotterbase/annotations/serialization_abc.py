import abc
from typing import Any

from spotterbase.rdf.types import TripleI


class JsonExportable(abc.ABC):
    @abc.abstractmethod
    def to_json(self) -> Any:
        ...


class JsonImportable(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_json(cls, json: Any) -> Any:
        ...


class TripleExportable(abc.ABC):
    @abc.abstractmethod
    def to_triples(self) -> TripleI:
        ...


class Portable(JsonExportable, JsonImportable, TripleExportable, abc.ABC):
    """ Supports the usually expected serialization/deserialization formats """
