"""
Code for running spotters over a corpus.

Currently, it is rather hacky. Possible improvements:
  * split into multiple files (core functionality vs. caller functions)
  * right now serialization is ntriples and results are simply copied. Can we do better?
"""

from __future__ import annotations

import dataclasses
import logging
import multiprocessing
import pickle
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator

from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.data.locator import TmpDir
from spotterbase.rdf import TripleI
from spotterbase.rdf.serializer import FileSerializer, NTriplesSerializer
from spotterbase.rdf.uri import Uri
from spotterbase.spotters.spotter import Spotter
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigUri, ConfigPath, ConfigInt
from spotterbase.utils.exit import DefaultSignalDelay
from spotterbase.utils.progress_updater import ProgressUpdater

logger = logging.getLogger()

DOCUMENT = ConfigUri('--document', 'The document to be processed by the spotter')
CORPUS = ConfigUri('--corpus', 'The corpus to be processed by the spotter')
NUMBER_OF_PROCESSES = ConfigInt('--number-of-processes', description='number of processes', default=4)
DIRECTORY = ConfigPath('--dir', 'Directory for the spotter results')


class _ProcessedDocTracker:
    def __init__(self, file: Path):
        self.file: Path = file
        # strings are more light-weight (we will have to keep them in memory)
        self.previously_processed_docs: set[str] = set()
        self.additionally_processed_docs_saved: set[str] = set()
        self.unsaved_processed_docs: set[str] = set()
        if self.file.exists():
            with open(self.file) as fp:
                for line in fp:
                    uri = line.strip()
                    if uri:
                        self.previously_processed_docs.add(uri)

    def filter_documents(self, documents: Iterable[Document]) -> Iterator[Document]:
        # should we also remove duplicates? (more complex/higher memory requirements)
        for document in documents:
            if str(document.get_uri()) not in self.previously_processed_docs:
                yield document

    def add(self, document: Uri | str):
        self.unsaved_processed_docs.add(str(document))

    def __enter__(self) -> _ProcessedDocTracker:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def save(self):
        if not self.unsaved_processed_docs:
            return
        with open(self.file, 'a') as fp:
            for doc in self.unsaved_processed_docs:
                fp.write(doc + '\n')
        self.additionally_processed_docs_saved.update(self.unsaved_processed_docs)
        self.unsaved_processed_docs = set()

    def __del__(self):
        assert not self.unsaved_processed_docs, 'Not all processed documents were saved'

    def remove(self):
        """ Remove file (should only be done when processing is finished) """
        # free up memory
        self.previously_processed_docs = set()
        self.additionally_processed_docs_saved = set()
        self.unsaved_processed_docs = set()
        self.file.unlink(missing_ok=True)


@dataclasses.dataclass
class _DocResult:
    files: dict[str, Path]    # spotter id -> path with pickled triples
    doc_uri: Uri


@dataclasses.dataclass
class _DocProcessor:
    spotters: list[Spotter]

    def process_doc(self, document: Document) -> _DocResult:
        result: dict[str, Path] = {}
        for spotter in self.spotters:
            try:
                path = TmpDir.get(spotter.spotter_short_id + '-' + uuid.uuid4().hex + '.nt')
                result[spotter.spotter_short_id] = path
                with open(path, 'w') as fp, NTriplesSerializer(fp) as serializer:
                    serializer.add_from_iterable(spotter.process_document(document))
            except Exception:
                logger.exception(f'{type(spotter)} raised an exception when processing {document.get_uri()}')
        return _DocResult(result, document.get_uri())


def run(spotter_classes: list[type[Spotter]], documents: Iterable[Document], *, corpus_descr: str, directory: Path):
    directory.mkdir(exist_ok=True)
    spotters: list[Spotter] = []
    serializers: dict[str, FileSerializer] = {}
    for spotter_class in spotter_classes:
        spotter_id = spotter_class.spotter_short_id
        assert spotter_id not in serializers

        spotter_ctx_path = directory / f'{spotter_id}-context.dmp'
        continuing: bool = spotter_ctx_path.is_file()

        triples: TripleI = iter(())
        if continuing:
            with open(spotter_ctx_path, 'rb') as fp:
                context = pickle.load(fp)
        else:
            context, triples = spotter_class.setup_run()
        spotters.append(spotter_class(context))

        rdf_file_path = directory / f'{spotter_id}.nt.gz'
        if not continuing and rdf_file_path.is_file():
            raise Exception(f'{rdf_file_path} already exists')
        serializer = FileSerializer(rdf_file_path, append=True)
        logger.info(f'{"Appending" if continuing else "Writing"} to {serializer.path}')
        serializers[spotter_id] = serializer
        if not continuing:
            serializer.write_comment(
                f'Results from spotter {spotter_class.spotter_short_id} over {corpus_descr} from {datetime.now()}'
            )
            serializer.write_comment('Triples from setup:')
            serializer.add_from_iterable(triples)
            serializer.flush()
            serializer.write_comment('Triples from processing actual content:')

    doc_tracker: _ProcessedDocTracker = _ProcessedDocTracker(directory / 'processed_docs.txt')
    if doc_tracker.previously_processed_docs:
        logger.info(f'{len(doc_tracker.previously_processed_docs)} documents were already processed '
                    f'according to {doc_tracker.file}')
    doc_processor: _DocProcessor = _DocProcessor(spotters)
    progress_updater = ProgressUpdater(message='{progress} documents were processed')

    try:
        with multiprocessing.Pool(processes=NUMBER_OF_PROCESSES.value) as pool:
            doc_result: _DocResult
            for i, doc_result in enumerate(pool.imap_unordered(doc_processor.process_doc, documents, chunksize=5)):
                progress_updater.update(i)
                with DefaultSignalDelay():
                    for spotter_id, path in doc_result.files.items():
                        with open(path) as fp:
                            for line in fp:
                                serializers[spotter_id].fp.write(line)
                        path.unlink()
                    doc_tracker.add(doc_result.doc_uri)
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt... Shutting down')
    finally:
        logger.info('Closing files')
        for serializer in serializers.values():
            serializer.close()
        doc_tracker.save()


def auto_run_spotter(spotter_class: type[Spotter] | list[type[Spotter]]):
    """ Runs the spotter(s) and handles all the command line arguments etc. """
    spotter_classes: list[type[Spotter]] = spotter_class if isinstance(spotter_class, list) else [spotter_class]

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
    directory = DIRECTORY.value
    assert directory is not None
    run(spotter_classes, documents_iterator, corpus_descr=str(uri), directory=directory)
