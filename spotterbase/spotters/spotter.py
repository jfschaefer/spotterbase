import abc

from spotterbase.corpora.interface import Document
from spotterbase.rdf.base import TripleI
from spotterbase.spotters.rdfhelpers import SpotterRun


class Spotter(abc.ABC):
    run: SpotterRun

    def __init__(self, run: SpotterRun):
        self.run = run

    @abc.abstractmethod
    def process_document(self, document: Document) -> TripleI:
        ...


