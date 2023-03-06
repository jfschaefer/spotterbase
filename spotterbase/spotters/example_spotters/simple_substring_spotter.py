import logging
import urllib.parse

from spotterbase.annotations.annotation import Annotation
from spotterbase.annotations.tag_body import MultiTagBody
from spotterbase.config_loader import ConfigInt
from spotterbase.corpora.interface import Document
from spotterbase.rdf.base import TripleI
from spotterbase.sb_vocab import SB
from spotterbase.spotters.spotter import Spotter

logger = logging.getLogger(__name__)

NUMBER_OF_PROCESSES = ConfigInt('--number-of-processes', description='number of processes', default=4)

SUBSTRINGS = ['ltx_unit']

SUBSTRING_URI = SB.NS['substring']


def get_contained_substrings(document: Document) -> list[str]:
    """ Returns contained substrings """
    try:
        with document.open() as fp:
            content = fp.read()
            return [s for s in SUBSTRINGS if s.encode('utf-8') in content]
    except Exception as e:
        logger.error(f'Encountered an unexpected error when processing {document.get_uri()}', exc_info=e)
        return []
    except UnicodeDecodeError as e:  # not an exception
        logger.error(f'Encountered an unexpected error when processing {document.get_uri()}', exc_info=e)
        return []


class SimpleSubstringSpotter(Spotter):
    spotter_short_id = 'ssubstr'

    def process_document(self, document: Document) -> TripleI:
        tag_uris = [SUBSTRING_URI / urllib.parse.quote_plus(tag) for tag in get_contained_substrings(document)]
        annotation = Annotation(uri=document.get_uri() + f'#{self.spotter_short_id}.anno',
                                target_uri=document.get_uri(),
                                body=MultiTagBody(tags=tag_uris),
                                creator_uri=self.ctx.run_uri)
        yield from annotation.to_triples()

# TODO: The following code should be into into general code for running a spotter

#     progress_logger = ProgressLogger(logger, 'Progress update: {progress} documents were processed')
#     with multiprocessing.Pool(NUMBER_OF_PROCESSES.value) as pool:
#         for i, result in enumerate(pool.imap(check, document_iterator(), chunksize=50)):
#             uri, substrings = result
#             for substring in substrings:
#                 annos[substring].add_target(uri)
#             progress_logger.update(i + 1)
#     logger.info(f'Processed a total of {i} documents')
#
#     for anno in annos.values():
#         yield from anno.triples()


# def main():
#     version = RELEASE_VERSION.value
#     assert version is not None
#     corpus = ArXMLivCorpus(version)
#     dest = DataDir.get(('centi-' if USE_CENTI_ARXIV else '') + f'arxmliv-substrings-{corpus.release}.ttl.gz')
#
#     with gzip.open(dest, 'wt') as fp:
#         fp.write(f'# Graph: {SB.NS["graph/arxmliv-substring-spotter"]:<>}\n')
#         with TurtleSerializer(fp) as serializer:
#             serializer.add_from_iterable(process(corpus))
#
#     logger.info(f'The graph has successfully been written to {dest}.')
