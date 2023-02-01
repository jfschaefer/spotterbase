from __future__ import annotations

from typing import Any, Optional

from spotterbase.annotations.body import Body
from spotterbase.annotations.conversion_base_classes import Portable
from spotterbase.annotations.target import Target
from spotterbase.rdf.base import Uri, TripleI
from spotterbase.rdf.vocab import RDF, OA, DCTerms


class Annotation(Portable):
    uri: Uri
    target: Target
    body: Body
    creator_uri: Optional[Uri]

    def __init__(self, uri: Uri, target: Target, body: Body, creator_uri: Optional[Uri] = None):
        self.uri = uri
        self.target = target
        self.body = body
        self.creator_uri = creator_uri

    def to_json(self) -> dict[str, Any]:
        json = {
            'id': str(self.uri),
            'target': self.target.to_json(),
            'body': self.body.to_json()
        }
        if self.creator_uri is not None:
            json['creator'] = str(self.creator_uri)
        return json

    @classmethod
    def from_json(cls, json: Any) -> Annotation:
        return Annotation(
            uri=Uri(json['id']),
            target=Target.from_json(json['target']),
            body=Body.from_json(json['body']),
            creator_uri=Uri(json['creator']) if 'creator' in json else None,
        )

    def to_triples(self) -> TripleI:
        yield self.uri, RDF.type, OA.Annotation
        yield from self.target.to_triples()
        yield self.uri, OA.hasTarget, self.target.uri
        yield from self.body.to_triples()
        yield self.uri, OA.hasBody, self.body.get_rdf_node()

        if self.creator_uri is not None:
            yield self.uri, DCTerms.creator, self.creator_uri
