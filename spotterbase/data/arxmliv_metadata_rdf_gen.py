import gzip
import logging
import zipfile
from typing import Optional

from spotterbase import config_loader
from spotterbase.config_loader import ConfigString
from spotterbase.data.arxiv import USE_CENTI_ARXIV
from spotterbase.data.arxmliv import ArXMLivConfig, ArXMLivUris, ArXMLivCorpus, ArXMLiv
from spotterbase.data.locator import DataDir
from spotterbase.data.rdf import SB, ArxivUris, ArXMLivUris
from spotterbase.rdf.base import TripleI
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import RDF
from spotterbase.spotters.utils import SpotterRun, Annotation
from spotterbase import __version__

logger = logging.getLogger(__name__)

RELEASE_VERSION = ConfigString('--arxmliv-release', description='arXMLiv release', choices=ArXMLivConfig.releases,
                               default=ArXMLivConfig.releases[-1])


def _get_severities_lists(corpus: ArXMLivCorpus) -> Optional[tuple[list[str], list[str], list[str]]]:
    if (path := corpus.path / 'meta' / 'grouped_by_severity.zip').is_file():
        with zipfile.ZipFile(path) as zf:
            with zf.open('no-problem-tasks.txt', 'r') as fp:
                np = [l.decode('utf-8').strip() for l in fp]
            with zf.open('warning-tasks.txt', 'r') as fp:
                w = [l.decode('utf-8').strip() for l in fp]
            with zf.open('error-tasks.txt', 'r') as fp:
                e = [l.decode('utf-8').strip() for l in fp]
            return np, w, e
    return None


def iter_triples(corpus: ArXMLivCorpus) -> TripleI:
    dataset_uri = ArXMLiv.get_release_uri(corpus.release)
    yield dataset_uri, RDF.type, SB.dataset
    yield dataset_uri, SB.basedOn, ArxivUris.dataset

    if USE_CENTI_ARXIV:
        logger.info(f'Note: Since `{USE_CENTI_ARXIV.name}` was set, most documents will be ignored')
    logger.info(f'Iterating over documents in {corpus.path}')
    for document in corpus:
        if USE_CENTI_ARXIV and not document.arxivid.is_in_centi_arxiv():
            continue
        yield document.get_uri(), SB.basedOn, document.arxivid.as_uri()
        yield document.get_uri(), RDF.type, SB.document
        yield document.get_uri(), SB.belongsTo, dataset_uri

    spotter_run = SpotterRun(SB.NS['spotter/arxmlivmetadata'], spotter_version=__version__)
    yield from spotter_run.triples()
    logger.info(f'Loading severity data')
    severities = _get_severities_lists(corpus)
    if severities:
        np, w, e = severities
        yield ArXMLivUris.severity_no_problem, RDF.type, ArXMLivUris.severity
        yield ArXMLivUris.severity_warning, RDF.type, ArXMLivUris.severity
        yield ArXMLivUris.severity_error, RDF.type, ArXMLivUris.severity
        for (docs, sev) in [(np, ArXMLivUris.severity_no_problem), (w, ArXMLivUris.severity_warning),
                            (e, ArXMLivUris.severity_error)]:
            annotation = Annotation(spotter_run)
            annotation.add_body(sev)
            for doc in docs:
                arxivid = corpus.filename_to_arxivid_or_none(doc)
                if arxivid:
                    if USE_CENTI_ARXIV and not arxivid.is_in_centi_arxiv():
                        continue
                    annotation.add_target(corpus.get_document(arxivid).get_uri())
                else:
                    logger.warning(f'Unexpected file name in severity data: {doc}')
            yield from annotation.triples()
    else:
        logger.warning(f'No severity data found in {corpus.path}')


def main():
    arxmliv = ArXMLiv()
    corpus = arxmliv.get_corpus(RELEASE_VERSION.value)
    dest = DataDir.get(('centi-' if USE_CENTI_ARXIV else '') + f'arxmliv-{corpus.release}.ttl.gz')
    with gzip.open(dest, 'wt') as fp:
        fp.write(f'# Graph: {ArXMLiv.get_graph_uri(RELEASE_VERSION.value):<>}\n')
        with TurtleSerializer(fp) as serializer:
            serializer.add_from_iterable(iter_triples(corpus))
    logger.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
