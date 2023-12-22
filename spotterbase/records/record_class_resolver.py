from __future__ import annotations

from typing import Optional, Iterable, Iterator

from spotterbase.records.record import Record
from spotterbase.rdf.uri import Uri


class RecordClassResolver:
    _lookup: dict[Uri, type[Record]]

    def __init__(self, record_types: Optional[Iterable[type[Record]]] = None):
        self._lookup = {}
        if record_types:
            for record_type in record_types:
                self.add(record_type)

    @classmethod
    def merged(cls, *record_class_resolvers: RecordClassResolver) -> RecordClassResolver:
        result = RecordClassResolver()
        for cr in record_class_resolvers:
            for record_type in cr.record_class_iter():
                result.add(record_type)
        return result

    def record_class_iter(self) -> Iterator[type[Record]]:
        yield from self._lookup.values()

    def __contains__(self, item):
        return item in self._lookup

    def __getitem__(self, item) -> type[Record]:
        try:
            return self._lookup[item]
        except KeyError:
            raise KeyError(f'Unknown record type: {item!r}')

    def add(self, record_type: type[Record]):
        type_ = record_type.record_info.record_type
        if type_ in self._lookup:
            if self._lookup[type_] != record_type:
                raise Exception(f'failed to map {type_} to {record_type.__qualname__} '
                                f'because it already refers to {self._lookup[type_].__qualname__}')
        self._lookup[type_] = record_type


DefaultRecordClassResolver = RecordClassResolver()
