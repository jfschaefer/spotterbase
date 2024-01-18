import gzip
import logging
import zipfile
from typing import Optional

from spotterbase import __version__
from spotterbase.corpora.resolver import Resolver
from spotterbase.data.locator import DataDir
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.annotation_creator import SpotterRun
from spotterbase.model_core.body import TagSet, Tag, SimpleTagBody
from spotterbase.model_core.corpus import CorpusInfo, DocumentInfo
from spotterbase.model_core.sb import SB
from spotterbase.plugins.arxiv.arxiv import ArxivUris
from spotterbase.plugins.arxiv.arxmliv import ArXMLivUris, ArXMLivCorpus, ARXMLIV_RELEASES
from spotterbase.rdf.serializer import NTriplesSerializer
from spotterbase.rdf.types import TripleI
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigString
from spotterbase.utils.progress_updater import ProgressUpdater

logger = logging.getLogger(__name__)

RELEASE_VERSION = ConfigString('--arxmliv-release', description='arXMLiv release', choices=ARXMLIV_RELEASES,
                               default=ARXMLIV_RELEASES[-1])


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


def iter_triples(corpus: ArXMLivCorpus, centi: bool = False) -> TripleI:
    corpus_uri = ArXMLivUris.get_corpus_uri(corpus.release)
    yield from CorpusInfo(uri=corpus_uri, label=f'arXMLiv {corpus.release}', based_on=ArxivUris.dataset).to_triples()

    logger.info(f'Iterating over documents in {corpus.get_path()}')
    progress_updater = ProgressUpdater('{progress} documents processed')
    for i, document in enumerate(corpus):
        if i % 1000 == 0:
            progress_updater.update(i)
        if centi and not document.arxivid.is_in_centi_arxiv():
            continue
        yield from DocumentInfo(uri=document.get_uri(), belongs_to=corpus_uri,
                                based_on=document.arxivid.as_uri()).to_triples()

    spotter_run = SpotterRun(SB.NS['spotter/arxmlivmetadata'], spotter_version=__version__)
    yield from spotter_run.to_triples()
    logger.info('Loading severity data')
    severities = _get_severities_lists(corpus)
    if severities:
        np, w, e = severities
        tag_set = TagSet(uri=ArXMLivUris.severity, label='ArXMLiv severity')
        yield from tag_set.to_triples()
        for sev_uri, label in [(ArXMLivUris.severity_no_problem, 'no problem'),
                               (ArXMLivUris.severity_warning, 'warning'),
                               (ArXMLivUris.severity_error, 'error')]:
            yield from Tag(uri=sev_uri, label=label, belongs_to=tag_set.uri).to_triples()

        progress_updater = ProgressUpdater('Created severity annotation for {progress} documents')
        i = 0
        for docs, sev in [(np, ArXMLivUris.severity_no_problem), (w, ArXMLivUris.severity_warning),
                          (e, ArXMLivUris.severity_error)]:
            for doc in docs:
                i += 1
                if i % 1000 == 0:
                    progress_updater.update(i)

                arxivid = corpus.filename_to_arxivid_or_none(doc)
                if arxivid:
                    if centi and not arxivid.is_in_centi_arxiv():
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
    print(repr(release_version))
    assert release_version is not None
    corpus = Resolver.get_corpus(ArXMLivUris.get_corpus_uri(release_version))
    assert isinstance(corpus, ArXMLivCorpus)
    for centi in [False, True]:
        dest = DataDir.get(('centi-' if centi else '') + f'arxmliv-{corpus.release}.nt.gz')
        logger.info(f'Creating {dest}.')
        with gzip.open(dest, 'wt') as fp:
            fp.write(
                f'# Graph: {ArXMLivUris.get_metadata_graph_uri(release_version) + ("-centi" if centi else ""):<>}\n'
            )
            with NTriplesSerializer(fp) as serializer:
                serializer.add_from_iterable(iter_triples(corpus, centi=centi))
        logger.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
