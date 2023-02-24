import gzip
import logging
import multiprocessing
from typing import Iterator

from spotterbase import config_loader
from spotterbase.config_loader import ConfigString, ConfigInt
from spotterbase.corpora.arxiv import USE_CENTI_ARXIV
from spotterbase.corpora.arxmliv import ArXMLivDocument, ArXMLivCorpus, ARXMLIV_RELEASES
from spotterbase.data.locator import DataDir
from spotterbase.sb_vocab import SB
from spotterbase.rdf.base import TripleI, BlankNode
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.literals import StringLiteral
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import RDF
from spotterbase.spotters.rdfhelpers import Annotation, SpotterRun
from spotterbase import __version__
from spotterbase.utils.logutils import ProgressLogger

logger = logging.getLogger(__name__)


RELEASE_VERSION = ConfigString('--arxmliv-release', description='arXMLiv release', choices=ARXMLIV_RELEASES,
                               default=ARXMLIV_RELEASES[-1])
NUMBER_OF_PROCESSES = ConfigInt('--number-of-processes', description='number of processes', default=4)


SUBSTRINGS = ['ltx_unit']

CONTAINED_SUBSTRING = SB.NS['containedSubstring']


def check(document: ArXMLivDocument) -> tuple[Uri, list[str]]:
    """ Returns document URI and contained substrings """
    try:
        with document.open() as fp:
            content = fp.read()
            return document.get_uri(), [s for s in SUBSTRINGS if s.encode('utf-8') in content]
    except Exception as e:
        logger.error(f'Encountered an unexpected error when processing {document.arxivid.identifier}', exc_info=e)
        return document.get_uri(), []
    except UnicodeDecodeError as e:    # not an exception
        logger.error(f'Encountered an unexpected error when processing {document.arxivid.identifier}', exc_info=e)
        return document.get_uri(), []


def process(corpus: ArXMLivCorpus) -> TripleI:
    spotter_run = SpotterRun(SB.NS['spotter/arxmlivsubstrings'], spotter_version=__version__)
    yield from spotter_run.triples()

    annos: dict[str, Annotation] = {}
    for substring in SUBSTRINGS:
        annos[substring] = Annotation(spotter_run)
        body = BlankNode()
        yield body, RDF.value, StringLiteral(substring)
        yield body, RDF.type, CONTAINED_SUBSTRING
        annos[substring].add_body(body)

    def document_iterator() -> Iterator[ArXMLivDocument]:
        if USE_CENTI_ARXIV:
            logger.info(f'Note: Since `{USE_CENTI_ARXIV.name}` was set, most documents will be ignored')
        for document in corpus:
            if not USE_CENTI_ARXIV or document.arxivid.is_in_centi_arxiv():
                yield document

    progress_logger = ProgressLogger(logger, 'Progress update: {progress} documents were processed')
    with multiprocessing.Pool(NUMBER_OF_PROCESSES.value) as pool:
        for i, result in enumerate(pool.imap(check, document_iterator(), chunksize=50)):
            uri, substrings = result
            for substring in substrings:
                annos[substring].add_target(uri)
            progress_logger.update(i + 1)
    logger.info(f'Processed a total of {i} documents')

    for anno in annos.values():
        yield from anno.triples()


def main():
    version = RELEASE_VERSION.value
    assert version is not None
    corpus = ArXMLivCorpus(version)
    dest = DataDir.get(('centi-' if USE_CENTI_ARXIV else '') + f'arxmliv-substrings-{corpus.release}.ttl.gz')

    with gzip.open(dest, 'wt') as fp:
        fp.write(f'# Graph: {SB.NS["graph/arxmliv-substring-spotter"]:<>}\n')
        with TurtleSerializer(fp) as serializer:
            serializer.add_from_iterable(process(corpus))

    logger.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
