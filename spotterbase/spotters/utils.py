import datetime
import logging
from typing import Optional

from spotterbase.data.rdf import SB
from spotterbase.rdf.base import Uri, TripleI, Object, BlankNode
from spotterbase.rdf.vocab import OA, RDF, DC
from spotterbase.rdf.literals import DateTimeLiteral, StringLiteral

logger = logging.getLogger(__name__)


class SpotterRun:
    def __init__(self, spotter_uri: Optional[Uri], spotter_version: Optional[str]):
        self.spotter_uri = spotter_uri
        self.spotter_version = spotter_version
        self.run_identifier = BlankNode()
        self.run_date = datetime.datetime.now()

    def triples(self) -> TripleI:
        yield self.run_identifier, RDF.type, SB.spotterRun
        yield self.run_identifier, SB.runDate, DateTimeLiteral(self.run_date)
        if self.spotter_uri:
            yield self.run_identifier, SB.withSpotter, self.spotter_uri
        if self.spotter_version:
            yield self.run_identifier, SB.spotterVersion, StringLiteral(self.spotter_version)


class Annotation:
    def __init__(self, spotter_run: Optional[SpotterRun] = None, annotation_uri: Optional[Uri] = None):
        self.spotter_run = spotter_run
        self.annotation_uri = annotation_uri or BlankNode()
        self.body: list[Object] = []
        self.target: list[Object] = []

    def add_body(self, body: Object):
        self.body.append(body)

    def add_target(self, target: Object):
        self.target.append(target)

    def triples(self) -> TripleI:
        if self.spotter_run:
            yield self.annotation_uri, DC.creator, self.spotter_run.run_identifier
        yield self.annotation_uri, RDF.type, OA.Annotation
        for t in self.target:
            yield self.annotation_uri, OA.hasTarget, t
        for b in self.body:
            yield self.annotation_uri, OA.hasBody, b
