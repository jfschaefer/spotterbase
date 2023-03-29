import gzip
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import IO

from spotterbase import __version__
from spotterbase.utils import config_loader
from spotterbase.anno_core.annotation import Annotation
from spotterbase.anno_core.annotation_creator import SpotterRun
from spotterbase.anno_core.tag_body import Tag, MultiTagBody, TagSet
from spotterbase.corpora.arxiv import ArxivId, ArxivCategory, USE_CENTI_ARXIV, ArxivUris
from spotterbase.data.locator import Locator, DataDir
from spotterbase.data.utils import json_lib
from spotterbase.rdf.literal import Uri
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import RDF
from spotterbase.anno_core.sb import SB

logger = logging.getLogger(__name__)

arxiv_raw_metadata_locator = Locator(
    '--arxiv-raw-metadata', 'path to the arxiv metadata OAI snapshot',
    ['arxiv-metadata-oai-snapshot.json', 'arxiv-metadata-oai-snapshot.json.zip'],
    'You can download it from https://www.kaggle.com/datasets/Cornell-University/arxiv')
arxiv_rdf_metadata_locator = Locator('--arxiv-rdf-gen-metadata', 'path to the arxiv metadata RDF file',
                                     ['arxiv-metadata.ttl.gz', 'centi-arxiv-metadata.ttl.gz'])


class MetatdataAccumulator(dict[ArxivId, list[str]]):
    # Note: accumulating all the data before creating the triples is not necessary anymore.
    # The current implementation could simply work on an entry-by-entry basis.
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

    def triples(self) -> TripleI:
        yield ArxivUris.dataset, RDF.type, SB.Dataset
        yield ArxivUris.centi_arxiv, RDF.type, SB.Dataset
        yield ArxivUris.centi_arxiv, SB.isSubsetOf, ArxivUris.dataset

        spotter_run = SpotterRun(uri=Uri.uuid(), spotter_uri=SB.NS['spotter/arxivmetadata'],
                                 spotter_version=__version__, date=datetime.now())
        yield from spotter_run.to_triples()

        tag_set = TagSet(uri=ArxivUris.topic_system)
        yield from tag_set.to_triples()

        known_cats: set[str] = set()
        for arxiv_id, cats in self.accumulator.items():
            # link to corpus
            uri = arxiv_id.as_uri()
            yield uri, RDF.type, SB.Document
            yield uri, SB.belongsTo, ArxivUris.dataset
            if arxiv_id.is_in_centi_arxiv():
                yield uri, SB.belongsTo, ArxivUris.centi_arxiv

            # deal with cats
            cat_set = set(cats)
            for cat in cats:
                if '.' in cat:
                    assert cat.count('.') == 1
                    cat_set.add(cat.split('.')[0])   # add super category
            for cat in cat_set:
                if cat not in known_cats:
                    yield from Tag(ArxivCategory(cat).as_uri(), belongs_to=tag_set.uri).to_triples()
                    known_cats.add(cat)

            # make annotation
            annotation = Annotation(arxiv_id.as_uri() + '#meta.cat.anno',
                                    target_uri=arxiv_id.as_uri(),
                                    body=MultiTagBody([ArxivCategory(cat).as_uri() for cat in cat_set]),
                                    creator_uri=spotter_run.uri)
            yield from annotation.to_triples()


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
