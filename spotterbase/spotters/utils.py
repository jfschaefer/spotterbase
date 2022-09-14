import datetime
import logging
from typing import Optional, Iterator

from rdflib import URIRef, BNode, RDF, Literal, DC
from rdflib.term import Identifier

from spotterbase.data.rdf import SB, OA
from spotterbase.rdf.base import Uri

logger = logging.getLogger(__name__)

TripleT = tuple[Identifier, Identifier, Identifier]


class SpotterRun:
    def __init__(self, spotter_uri: Optional[URIRef], spotter_version: Optional[str]):
        self.spotter_uri = spotter_uri
        self.spotter_version = spotter_version
        self.run_identifier = BNode()
        self.run_date = datetime.datetime.now()

    def triples(self) -> Iterator[TripleT]:
        yield self.run_identifier, RDF.type, SB.spotterRun
        yield self.run_identifier, SB.runDate, Literal(self.run_date)
        if self.spotter_uri:
            yield self.run_identifier, SB.withSpotter, self.spotter_uri
        if self.spotter_version:
            yield self.run_identifier, SB.spotterVersion, Literal(self.spotter_version)


class Annotation:
    def __init__(self, spotter_run: Optional[SpotterRun] = None, annotation_uri: Optional[Identifier] = None):
        self.spotter_run = spotter_run
        self.annotation_uri = annotation_uri or BNode()
        self.body: list[Identifier] = []
        self.target: list[Identifier] = []

    def add_body(self, body: Identifier):
        self.body.append(body)

    def add_target(self, target: Uri | Identifier):
        if isinstance(target, Uri):
            target = target.as_uriref()
        self.target.append(target)

    def triples(self) -> Iterator[TripleT]:
        if self.spotter_run:
            yield self.annotation_uri, DC.creator, self.spotter_run.run_identifier
        yield self.annotation_uri, RDF.type, OA.Annotation
        for t in self.target:
            yield self.annotation_uri, OA.hasTarget, t
        for b in self.body:
            yield self.annotation_uri, OA.hasBody, b
