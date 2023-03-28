import logging
from datetime import datetime
from typing import Iterable

from spotterbase import config_loader
from spotterbase.config_loader import ConfigUri, ConfigPath, ConfigInt
from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.data.locator import DataDir
from spotterbase.rdf.serializer import FileSerializer
from spotterbase.rdf.uri import Uri
from spotterbase.spotters.spotter import Spotter
from spotterbase.utils.logutils import ProgressLogger

logger = logging.getLogger()

DOCUMENT = ConfigUri('--document', 'The document to be processed by the spotter')
CORPUS = ConfigUri('--corpus', 'The corpus to be processed by the spotter')
RESULT_FILE = ConfigPath(
    '--result-file', f'File for the spotter results (default: {DataDir.get("[SPOTTER]-run-[TIMESTAMP].ttl.gz")})'
)
NUMBER_OF_PROCESSES = ConfigInt('--number-of-processes', description='number of processes', default=4)


def run(spotter_class: type[Spotter], documents_iterator: Iterable[Document], source: Uri):
    # TODO: multiprocessing
    if RESULT_FILE.value is None:
        path = DataDir.get(
            f'{spotter_class.spotter_short_id}-run-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.ttl.gz'
        )
    else:
        path = RESULT_FILE.value
    if path.is_file():
        raise Exception(f'{path} already exists')

    with FileSerializer(path) as serializer:
        serializer.write_comment(
            f'Results from spotter {spotter_class.spotter_short_id} over {source} from {datetime.now()}')
        context, triples = spotter_class.setup_run()
        serializer.write_comment('Triples from setup:')
        serializer.add_from_iterable(triples)
        serializer.flush()
        serializer.write_comment('Triples from processing actual content:')
        spotter = spotter_class(context)

        progress_logger = ProgressLogger(logger, 'Status update: Processed {progress} documents')
        for i, document in enumerate(documents_iterator):
            serializer.add_from_iterable(spotter.process_document(document))
            progress_logger.update(i)


def main(spotter: type[Spotter]):
    config_loader.auto()
    if DOCUMENT.value is not None:
        if CORPUS.value is not None:
            raise Exception(f'Cannot have values for both {DOCUMENT.name} and {CORPUS.name}')
        document = Resolver.get_document(DOCUMENT.value)
        if document is None:
            raise Exception(f'Failed to find document {document}')
        documents_iterator = iter([document])
    else:
        if CORPUS.value is None:
            raise Exception('No corpus or document was specified')
        corpus = Resolver.get_corpus(CORPUS.value)
        if corpus is None:
            raise Exception(f'Failed to find corpus {corpus}')
        documents_iterator = iter(corpus)

    uri = DOCUMENT.value or CORPUS.value
    assert uri is not None
    run(spotter, documents_iterator, uri)
