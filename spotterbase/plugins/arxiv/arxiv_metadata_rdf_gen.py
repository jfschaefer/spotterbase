import dataclasses
import functools
import gzip
import logging
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import IO, Iterable, Optional

import requests
from lxml import etree
from lxml.etree import _Element

from spotterbase import __version__
from spotterbase.data import fast_json
from spotterbase.data.locator import Locator
from spotterbase.model_core.annotation import Annotation
from spotterbase.model_core.annotation_creator import SpotterRun
from spotterbase.model_core.body import Tag, MultiTagBody, TagSet
from spotterbase.model_core.corpus import CorpusInfo, DocumentInfo
from spotterbase.model_core.sb import SB
from spotterbase.plugins.arxiv.arxiv import ArxivId, ArxivCategory, ArxivUris
from spotterbase.plugins.model_extra.corpus_frac import FRAC_CORPUS
from spotterbase.rdf import Uri
from spotterbase.rdf.serializer import NTriplesSerializer
from spotterbase.rdf.types import TripleI
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigPath
from spotterbase.utils.progress_updater import ProgressUpdater

logger = logging.getLogger(__name__)

arxiv_raw_metadata_locator = Locator(
    '--arxiv-raw-metadata', 'path to the arxiv metadata OAI snapshot',
    ['arxiv-metadata-oai-snapshot.json', 'arxiv-metadata-oai-snapshot.json.zip'],
    'You can download it from https://www.kaggle.com/datasets/Cornell-University/arxiv')
destination = ConfigPath('--dest', 'destination directory', default='.')


@dataclasses.dataclass(slots=True)
class DocumentEntry:
    arxiv_id: ArxivId
    title: str
    categories: list[str]
    license: Optional[Uri] = None


def entries_from_io(file: IO) -> Iterable[DocumentEntry]:
    progress_updater = ProgressUpdater('{progress} entries loaded')
    for i, line in enumerate(file):
        if i % 1000 == 0:
            progress_updater.update(i)
        entry = fast_json.loads(line)
        arxiv_id = ArxivId(entry['id'])
        if 'categories' in entry and entry['categories']:
            yield DocumentEntry(
                arxiv_id,
                title=entry['title'],
                categories=entry['categories'].split(),
                license=Uri(entry['license']) if entry['license'] else None
            )


def entries_from_file(path: Path) -> Iterable[DocumentEntry]:
    if path.name.endswith('.zip'):
        with zipfile.ZipFile(path) as zf:
            with zf.open('arxiv-metadata-oai-snapshot.json') as fp:
                yield from entries_from_io(fp)
    else:
        with open(path) as fp:
            yield from entries_from_io(fp)


@functools.cache
def get_arxiv_website() -> _Element:
    logger.info('Downloading the arxiv website in order to get category labels')
    response = requests.get('https://arxiv.org')
    response.raise_for_status()
    return etree.parse(BytesIO(response.content), parser=etree.HTMLParser()).getroot()  # type: ignore


@functools.cache
def get_arxiv_cat_label(cat: str) -> Optional[str]:
    """Note: this is very brittle as it depends on the arxiv website"""
    website = get_arxiv_website()
    if r := website.xpath(f'//a[@id="main-{cat}"]'):   # top-level category
        return r[0].text.strip()  # type: ignore
    r = website.xpath(f'//a[@id="{cat}"]')    # sub-category
    if not r:
        # happens for defunct categories (e.g. 'acc-phys'), but in those cases the new category is also supplied
        # in a few cases it also happens if the parent category is skipped for some reason
        # (e.g. acc-ph instead of physics.acc-ph). We'll just ignore those cases.
        return None
    return r[0].text.strip()    # type: ignore


def make_triples(entries: Iterable[DocumentEntry]) -> TripleI:
    yield from CorpusInfo(
        ArxivUris.dataset,
        label='arxiv',
        comment='The arxiv corpus. Note that documents are "abstract" arxiv papers, and not in any specific format.'
    ).to_triples()

    spotter_run = SpotterRun(uri=Uri.uuid(), spotter_uri=SB.NS['spotter/arxivmetadata'],
                             spotter_version=__version__, date=datetime.now())
    yield from spotter_run.to_triples()

    tag_set = TagSet(uri=ArxivUris.topic_system)
    yield from tag_set.to_triples()

    known_cats: set[str] = set()
    progress_updater = ProgressUpdater('Created triples for {progress} entries')
    for i, entry in enumerate(entries):
        if i % 1000 == 0:
            progress_updater.update(i)
        arxiv_id = entry.arxiv_id
        uri = arxiv_id.as_uri()
        yield from DocumentInfo(uri=uri, belongs_to=ArxivUris.dataset).to_triples()

        # deal with cats
        cat_set = set(set(entry.categories))
        for cat in cat_set:
            if cat not in known_cats:
                parent_cat: Optional[str] = None
                if '.' in cat:
                    assert cat.count('.') == 1
                    parent_cat = cat.split('.')[0]
                    if parent_cat not in known_cats:
                        yield from Tag(ArxivCategory(parent_cat).as_uri(), belongs_to=tag_set.uri,
                                       label=get_arxiv_cat_label(parent_cat) or parent_cat).to_triples()
                        known_cats.add(parent_cat)

                yield from Tag(
                    ArxivCategory(cat).as_uri(), belongs_to=tag_set.uri,
                    label=get_arxiv_cat_label(cat) or cat,
                    sub_tag_of=ArxivCategory(parent_cat).as_uri() if parent_cat is not None else None
                ).to_triples()
                known_cats.add(cat)

        # make cat annotation
        yield from Annotation(
            arxiv_id.as_uri() + '#meta.cat.anno',
            target_uri=arxiv_id.as_uri(),
            body=MultiTagBody([ArxivCategory(cat).as_uri() for cat in cat_set]),
            creator_uri=spotter_run.uri
        ).to_triples()

        if arxiv_id.is_in_deci_arxiv():
            # sub-corpus annotation
            yield from Annotation(
                arxiv_id.as_uri() + '#meta.subcorpus.anno',
                target_uri=arxiv_id.as_uri(),
                body=MultiTagBody(
                    [
                        uri for (uri, relevant) in [
                            (FRAC_CORPUS.deci, arxiv_id.is_in_deci_arxiv()),
                            (FRAC_CORPUS.centi, arxiv_id.is_in_centi_arxiv()),
                            (FRAC_CORPUS.milli, arxiv_id.is_in_milli_arxiv()),
                            (FRAC_CORPUS.decimilli, arxiv_id.is_in_decimilli_arxiv()),
                        ] if relevant
                    ]
                ),
                creator_uri=spotter_run.uri
            ).to_triples()


def main():
    path = arxiv_raw_metadata_locator.require()
    logger.info(f'Loading the arxiv metadata from {path}. This will take a moment.')
    entries = list(entries_from_file(path))
    logger.info(f'Loaded the metadata of {len(entries)} arxiv documents.')

    dest_dir = destination.value
    assert dest_dir is not None
    dest_dir.mkdir(exist_ok=True)

    for dest, graph, triple_i in [
        (dest_dir / 'arxiv-metadata.nt.gz', ArxivUris.meta_graph, make_triples(entries)),
        (dest_dir / 'arxiv-metadata-centi.nt.gz', ArxivUris.meta_graph + '-centi',
         make_triples(e for e in entries if e.arxiv_id.is_in_centi_arxiv())),
    ]:
        logger.info(f'Writing graph to {dest}.')
        with gzip.open(dest, 'wt') as fp:
            fp.write(f'# Graph: {graph:<>}\n')
            serializer = NTriplesSerializer(fp)
            serializer.add_from_iterable(triple_i)
            serializer.flush()
        logger.info(f'The graph has successfully been written to {dest}.')


if __name__ == '__main__':
    config_loader.auto()
    main()
