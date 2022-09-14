import gzip
import logging
import multiprocessing
from typing import Iterator

import rdflib
from rdflib import BNode, RDF, Literal

from spotterbase import config_loader
from spotterbase.config_loader import ConfigString, ConfigInt
from spotterbase.data.arxiv import USE_CENTI_ARXIV
from spotterbase.data.arxmliv import ArXMLivConfig, ArXMLiv, ArXMLivDocument, ArXMLivCorpus
from spotterbase.data.locator import DataDir
from spotterbase.data.rdf import SB
from spotterbase.rdf.base import Uri
from spotterbase.spotters.utils import Annotation, TripleT, SpotterRun
from spotterbase.utils import version_string, ProgressLogger

logger = logging.getLogger(__name__)


RELEASE_VERSION = ConfigString('--arxmliv-release', description='arXMLiv release', choices=ArXMLivConfig.releases,
                               default=ArXMLivConfig.releases[-1])
NUMBER_OF_PROCESSES = ConfigInt('--number-of-processes', description='number of processes', default=4)


SUBSTRINGS = ['ltx_unit']

CONTAINS_SUBSTRING = SB.NS['containsSubstring']


def check(document: ArXMLivDocument) -> tuple[Uri, list[str]]:
    """ Returns document URI and contained substrings """
    try:
        with document.open() as fp:
            content = fp.read()
            return document.get_uri(), [s for s in SUBSTRINGS if s.encode('utf-8') in content]
    except Exception as e:
        logging.error(f'Encountered an unexpected error when processing {document.arxivid.identifier}', exc_info=e)
        return document.get_uri(), []
    except UnicodeDecodeError as e:    # not an exception
        logging.error(f'Encountered an unexpected error when processing {document.arxivid.identifier}', exc_info=e)
        return document.get_uri(), []


def process(corpus: ArXMLivCorpus) -> Iterator[TripleT]:
    spotter_run = SpotterRun(SB['spotter/arxmlivsubstrings'], spotter_version=version_string())
    yield from spotter_run.triples()

    annos: dict[str, Annotation] = {}
    for substring in SUBSTRINGS:
        annos[substring] = Annotation(spotter_run)
        body = BNode()
        yield body, RDF.value, Literal(substring)
        yield body, RDF.type, CONTAINS_SUBSTRING
        annos[substring].add_body(body)

    def document_iterator() -> Iterator[ArXMLivDocument]:
        if USE_CENTI_ARXIV:
            logging.info(f'Note: Since `{USE_CENTI_ARXIV.name}` was set, most documents will be ignored')
        for document in corpus:
            if not USE_CENTI_ARXIV or document.arxivid.is_in_centi_arxiv():
                yield document

        # for document in corpus
    progress_logger = ProgressLogger(logger, 'Progress update: {progress} documents were processed')
    with multiprocessing.Pool(NUMBER_OF_PROCESSES.value) as pool:
        for i, result in enumerate(pool.imap(check, document_iterator(), chunksize=50)):
            uri, substrings = result
            for substring in substrings:
                annos[substring].add_target(uri.as_uriref())
            progress_logger.update(i+1)
    logger.info(f'Processed a total of {i} documents')

    for anno in annos.values():
        yield from anno.triples()


def main():
    arxmliv = ArXMLiv()
    corpus = arxmliv.get_corpus(RELEASE_VERSION.value)
    graph = rdflib.Graph()
    for triple in process(corpus):
        graph.add(triple)

    dest = DataDir.get(('centi-' if USE_CENTI_ARXIV else '') + f'arxmliv-substrings-{corpus.release}.ttl.gz')
    logging.info(f'Writing graph to {dest}.')
    with gzip.open(dest, 'wb') as fp:
        graph.serialize(fp)
    logging.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
