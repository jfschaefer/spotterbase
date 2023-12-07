import gzip
import logging
import zipfile
from typing import Optional

from spotterbase.utils import config_loader
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.annotation_creator import SpotterRun
from spotterbase.model_core.body import TagSet, Tag, SimpleTagBody
from spotterbase.utils.config_loader import ConfigString
from spotterbase.corpora.arxiv import USE_CENTI_ARXIV, ArxivUris
from spotterbase.corpora.arxmliv import ArXMLivUris, ArXMLivCorpus, ARXMLIV_RELEASES
from spotterbase.corpora.resolver import Resolver
from spotterbase.data.locator import DataDir
from spotterbase.model_core.sb import SB
from spotterbase.rdf.types import TripleI
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import RDF
from spotterbase import __version__

logger = logging.getLogger(__name__)

RELEASE_VERSION = ConfigString('--arxmliv-release', description='arXMLiv release', choices=ARXMLIV_RELEASES,
                               default=ARXMLIV_RELEASES)


def _get_severities_lists(corpus: ArXMLivCorpus) -> Optional[tuple[list[str], list[str], list[str]]]:
    if (path := corpus.get_path() / 'meta' / 'grouped_by_severity.zip').is_file():
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
    dataset_uri = ArXMLivUris.get_corpus_uri(corpus.release)
    yield dataset_uri, RDF.type, SB.Dataset
    yield dataset_uri, SB.isBasedOn, ArxivUris.dataset

    if USE_CENTI_ARXIV:
        logger.info(f'Note: Since `{USE_CENTI_ARXIV.name}` was set, most documents will be ignored')
    logger.info(f'Iterating over documents in {corpus.get_path()}')
    for document in corpus:
        if USE_CENTI_ARXIV and not document.arxivid.is_in_centi_arxiv():
            continue
        yield document.get_uri(), SB.isBasedOn, document.arxivid.as_uri()
        yield document.get_uri(), RDF.type, SB.Document
        yield document.get_uri(), SB.belongsTo, dataset_uri

    spotter_run = SpotterRun(SB.NS['spotter/arxmlivmetadata'], spotter_version=__version__)
    yield from spotter_run.to_triples()
    logger.info('Loading severity data')
    severities = _get_severities_lists(corpus)
    if severities:
        np, w, e = severities
        tag_set = TagSet(uri=ArXMLivUris.severity)
        yield from tag_set.to_triples()
        for sev_uri in [ArXMLivUris.severity_no_problem, ArXMLivUris.severity_warning, ArXMLivUris.severity_error]:
            yield from Tag(uri=sev_uri, belongs_to=tag_set.uri).to_triples()

        for (docs, sev) in [(np, ArXMLivUris.severity_no_problem), (w, ArXMLivUris.severity_warning),
                            (e, ArXMLivUris.severity_error)]:
            for doc in docs:
                arxivid = corpus.filename_to_arxivid_or_none(doc)
                if arxivid:
                    if USE_CENTI_ARXIV and not arxivid.is_in_centi_arxiv():
                        continue
                else:
                    logger.warning(f'Unexpected file name in severity data: {doc}')
                    continue
                doc_uri = corpus.get_document_by_id(arxivid).get_uri()
                annotation = Annotation(uri=doc_uri + '#meta.severity.anno')
                annotation.target_uri = doc_uri
                annotation.creator_uri = spotter_run.uri
                annotation.body = SimpleTagBody(tag=sev)
                yield from annotation.to_triples()
    else:
        logger.warning(f'No severity data found in {corpus.get_path()}')


def main():
    release_version = RELEASE_VERSION.value
    assert release_version is not None
    corpus = Resolver.get_corpus(ArXMLivUris.get_corpus_uri(release_version))
    assert isinstance(corpus, ArXMLivCorpus)
    dest = DataDir.get(('centi-' if USE_CENTI_ARXIV else '') + f'arxmliv-{corpus.release}.ttl.gz')
    with gzip.open(dest, 'wt') as fp:
        fp.write(f'# Graph: {ArXMLivUris.get_metadata_graph_uri(release_version):<>}\n')
        with TurtleSerializer(fp) as serializer:
            serializer.add_from_iterable(iter_triples(corpus))
    logger.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
