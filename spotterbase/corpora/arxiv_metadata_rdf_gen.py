import gzip
import logging
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import IO

from spotterbase import config_loader
from spotterbase.corpora.arxiv import ArxivId, ArxivCategory, USE_CENTI_ARXIV, ArxivUris
from spotterbase.data.locator import Locator, DataDir
from spotterbase.sb_vocab import SB
from spotterbase.data.utils import json_lib
from spotterbase.rdf.base import TripleI
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import RDF
from spotterbase.spotters.rdfhelpers import Annotation, SpotterRun
from spotterbase import __version__

logger = logging.getLogger(__name__)

arxiv_raw_metadata_locator = Locator('--arxiv-raw-metadata', 'path to the arxiv metadata OAI snapshot',
                                     ['arxiv-metadata-oai-snapshot.json', 'arxiv-metadata-oai-snapshot.json.zip'],
                                     'You can download it from https://www.kaggle.com/datasets/Cornell-University/arxiv')
arxiv_rdf_metadata_locator = Locator('--arxiv-rdf-gen-metadata', 'path to the arxiv metadata RDF file',
                                     ['arxiv-metadata.ttl.gz', 'centi-arxiv-metadata.ttl.gz'])


class MetatdataAccumulator(dict[ArxivId, list[str]]):
    def __init__(self):
        super().__init__()

    def load_from_io(self, file: IO):
        json = json_lib()
        if USE_CENTI_ARXIV:
            logger.info(f'Note: Since `{USE_CENTI_ARXIV.name}` was set, most documents will be ignored')
        for line in file:
            entry = json.loads(line)
            arxiv_id = ArxivId(entry['id'])
            if USE_CENTI_ARXIV and not arxiv_id.is_in_centi_arxiv():
                continue
            if arxiv_id in self:
                logger.warning(f'Multiple entries for {arxiv_id}')
            if 'categories' in entry and entry['categories']:
                self[arxiv_id] = entry['categories'].split()

    def load_from_file(self, path: Path):
        if path.name.endswith('.zip'):
            with zipfile.ZipFile(path) as zf:
                with zf.open('arxiv-metadata-oai-snapshot.json') as fp:
                    self.load_from_io(fp)
        else:
            with open(path) as fp:
                self.load_from_io(fp)


class MetadataRdfGenerator:
    def __init__(self, accumulator: MetatdataAccumulator):
        self.accumulator = accumulator

    def _highlevel(self) -> TripleI:
        yield ArxivUris.dataset, RDF.type, SB.dataset
        yield ArxivUris.centi_arxiv, RDF.type, SB.dataset
        yield ArxivUris.centi_arxiv, SB.subset, ArxivUris.dataset

    def triples(self) -> TripleI:
        # Yielding triples and then discarding built-up corpora structures reduces the memory requirements

        yield from self._highlevel()

        spotter_run = SpotterRun(SB.NS['spotter/arxivmetadata'], spotter_version=__version__)
        yield from spotter_run.triples()

        # re-arrange corpora
        cat_to_arxivid: defaultdict[str, list[ArxivId]] = defaultdict(list)
        for arxiv_id, cats in self.accumulator.items():
            for cat in cats:
                cat_to_arxivid[cat].append(arxiv_id)

        for cat in cat_to_arxivid:
            cat_uri = ArxivCategory(cat).as_uri()
            yield cat_uri, RDF.type, SB.topic
            yield cat_uri, SB.belongsTo, ArxivUris.topic_system
            if '.' in cat:
                assert cat.count('.') == 1
                supercat = cat.split('.')[0]
                yield cat_uri, SB.subtopicOf, ArxivCategory(supercat).as_uri()

        # annotations
        for cat, arxiv_ids in cat_to_arxivid.items():
            # Single annotation with lots of targets to reduce number of triples
            annotation = Annotation(spotter_run)
            for arxiv_id in arxiv_ids:
                annotation.add_target(arxiv_id.as_uri())
            annotation.add_body(ArxivCategory(cat).as_uri())
            yield from annotation.triples()

        for arxiv_id in self.accumulator:
            uri = arxiv_id.as_uri()
            yield uri, RDF.type, SB.document
            yield uri, SB.belongsTo, ArxivUris.dataset
            if arxiv_id.is_in_centi_arxiv():
                yield uri, SB.belongsTo, ArxivUris.centi_arxiv


def _get_rdf_dest() -> Path:
    if arxiv_rdf_metadata_locator.specified_location:
        dest = arxiv_rdf_metadata_locator.require()
        if dest.name.startswith('centi') and not USE_CENTI_ARXIV:
            logger.warning(f'RDF destination ({str(dest)}) starts with "centi", but the whole arxiv is included')
        return dest
    return DataDir.get(('centi-' if USE_CENTI_ARXIV else '') + 'arxiv-metadata.ttl.gz')


def main():
    accumulator = MetatdataAccumulator()
    path = arxiv_raw_metadata_locator.require()
    logger.info(f'Loading the arxiv metadata from {path}. This will take a moment.')
    accumulator.load_from_file(path)
    logger.info(f'Loaded the metadata of {len(accumulator)} arxiv documents.')

    dest = _get_rdf_dest()
    logger.info(f'Writing graph to {dest}.')
    with gzip.open(dest, 'wt') as fp:
        fp.write(f'# Graph: {ArxivUris.meta_graph:<>}\n')
        serializer = TurtleSerializer(fp)
        serializer.add_from_iterable(MetadataRdfGenerator(accumulator).triples())
        serializer.flush()
    logger.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
