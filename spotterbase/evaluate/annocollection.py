from __future__ import annotations

import dataclasses

from spotterbase.model_core import Annotation, FragmentTarget
from spotterbase.rdf import Uri
from spotterbase.records.record import Record


@dataclasses.dataclass(frozen=True)
class AnnoWithFragTarget:
    anno: Annotation
    target: FragmentTarget

    def __post_init__(self):
        if self.anno.target_uri != self.target.uri:
            raise ValueError(f'Annotation target URI {self.anno.target_uri} '
                             f'does not match FragmentTarget URI {self.target.uri}')


@dataclasses.dataclass
class AnnoCollection:
    fragment_annos_by_source: dict[Uri, list[AnnoWithFragTarget]] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_records(cls, records: list[Record]) -> AnnoCollection:
        record_by_uri = {}
        for record in records:
            if record.uri in record_by_uri:
                raise ValueError(f'Duplicate record URI: {record.uri}')
            record_by_uri[record.uri] = record

        fragment_annos_by_source: dict[Uri, list[AnnoWithFragTarget]] = {}
        for record in records:
            if not isinstance(record, Annotation):
                continue

            if record.target_uri in record_by_uri:
                target = record_by_uri[record.target_uri]
                if isinstance(target, FragmentTarget):
                    fragment_annos_by_source.setdefault(target.source, []).append(AnnoWithFragTarget(record, target))
                    continue

            raise ValueError(f'Annotation target {record.target_uri} not yet supported')

        return cls(fragment_annos_by_source)
