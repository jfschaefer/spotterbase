import logging
import urllib.parse

from spotterbase.anno_core.annotation import Annotation
from spotterbase.anno_core.tag_body import MultiTagBody, Tag, TagSet
from spotterbase.corpora.interface import Document
from spotterbase.rdf import Uri
from spotterbase.rdf.types import TripleI
from spotterbase.anno_core.sb import SB
from spotterbase.spotters.spotter import Spotter, SpotterContext

logger = logging.getLogger(__name__)


SUBSTRINGS = ['ltx_unit', 'ltx_theorem']

TAG_SET = TagSet(uri=SB.NS['docsubstrings'],
                 label='Document Substrings',
                 comment='Used to tag documents that contain a particular substring '
                         '(e.g. to pre-select documents that are interesting for a spotter)')

TAGS: dict[str, Tag] = {
    ss: Tag(uri=TAG_SET.uri + '#' + urllib.parse.quote_plus(ss), label=ss, belongs_to=TAG_SET.uri,
            comment=f'Document contains the string {ss!r}')
    for ss in SUBSTRINGS
}

SUBSTRING_URI = SB.NS['substring']


def get_contained_substrings(document: Document) -> list[str]:
    """ Returns contained substrings """
    try:
        with document.open('rb') as fp:
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

    @classmethod
    def setup_run(cls, **kwargs) -> tuple[SpotterContext, TripleI]:
        ctx = SpotterContext(run_uri=Uri.uuid())

        def triple_gen() -> TripleI:
            yield from TAG_SET.to_triples()
            for tag in TAGS.values():
                yield from tag.to_triples()

        return ctx, triple_gen()

    def process_document(self, document: Document) -> TripleI:
        tag_uris: list[Uri] = [TAGS[ss].uri for ss in get_contained_substrings(document)]
        annotation = Annotation(uri=document.get_uri() + f'#{self.spotter_short_id}.anno',
                                target_uri=document.get_uri(),
                                body=MultiTagBody(tags=tag_uris),
                                creator_uri=self.ctx.run_uri)
        yield from annotation.to_triples()


if __name__ == '__main__':
    from spotterbase.spotters import spotter_runner
    spotter_runner.auto_run_spotter(SimpleSubstringSpotter)
