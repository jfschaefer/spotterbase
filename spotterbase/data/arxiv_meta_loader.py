import argparse
import gzip
import logging
import zipfile
from typing import IO

import rdflib
from rdflib.plugins.serializers.turtle import TurtleSerializer

from spotterbase import config_loader
from spotterbase.data.arxiv_metadata import ArxivId, REL_HAS_CATEGORY, ArxivCategory, REL_SUBCATEGORY_OF, \
    USE_CENTI_ARXIV
from spotterbase.data.locator import Locator
from spotterbase.data.utils import json_lib

logger = logging.getLogger(__name__)

arxiv_raw_metadata_locator = Locator('--arxiv-raw-metadata', 'path to the arxiv metadata OAI snapshot',
                                     ['arxiv-metadata-oai-snapshot.json', 'arxiv-metadata-oai-snapshot.json.zip'],
                                     'You can download it from https://www.kaggle.com/datasets/Cornell-University/arxiv')
arxiv_rdf_metadata_locator = Locator('--arxiv-rdf-metadata', 'path to the arxiv metadata RDF file',
                                     ['arxiv-metadata.rdf'])


def _generate_rdf_from_io(file: IO):
    graph = rdflib.Graph()
    json = json_lib()
    i = -1
    discovered_cats: set[str] = set()
    for i, line in enumerate(file):
        if not i % 10000:
            print(i)
        entry = json.loads(line)
        arxiv_id = ArxivId(entry['id'])
        if USE_CENTI_ARXIV and not arxiv_id.is_in_centi_arxiv():
            continue

        if 'categories' in entry and entry['categories']:
            for cat in entry['categories'].split():
                discovered_cats.add(cat)
                graph.add((arxiv_id.as_uri(), REL_HAS_CATEGORY, ArxivCategory(cat).as_uri()))

    # add sub-category edges
    for cat in discovered_cats:
        if '.' in cat:
            assert cat.count('.') == 1
            supercat = cat.split('.')[0]
            graph.add((ArxivCategory(cat).as_uri(), REL_SUBCATEGORY_OF, ArxivCategory(supercat).as_uri()))

    logging.info(f'Processed the metadata of {i + 1} arxiv documents, resulting in {len(graph)} triples')

    dest = '/tmp/test.ttl.gz'
    logging.info(f'Writing the graph to {dest}')

    serializer = TurtleSerializer(graph)
    with gzip.open(dest, 'wb') as fp:
        serializer.serialize(fp)

    # graph.serialize(dest, format='turtle')


# def _use_prefix(prefix: str, namespace: rdflib.Namespace, uri: rdflib.URIRef):
#     s = str(uri)
#     n = str(namespace)
#     assert s.startswith(n)
#     return f'{prefix}:{s[len(n):]}'

# def _generate_rdf_from_io(file: IO):
#     """ reads the metadata from ``file`` and writes into a compressed turtle file.
#         It doesn't use rdflib because that would
#     """
#     json = json_lib()
#     i = -1
#     dest = '/tmp/test.ttl.gz'
#     with gzip.open(dest, 'wt') as fp:
#         fp.write(f'@prefix rel: <{str(REL_NAMESPACE)}>.\n')
#         fp.write(f'@prefix i: <{str(ArxivId.uri_namespace)}>.\n')
#         fp.write(f'@prefix c: <{str(ArxivCategory.uri_namespace)}>.\n\n')
#         prefixed_has_cat = _use_prefix('rel', REL_NAMESPACE, REL_HAS_CATEGORY)
#         for i, line in enumerate(file):
#             if i == 10e4:
#                 break
#             entry = json.loads(line)
#             doc_uri = ArxivId(entry['id']).as_uri()
#             cats = []
#             if 'categories' in entry and entry['categories']:
#                 cats = [ArxivCategory(cat).as_uri() for cat in entry['categories'].split()]
#             if cats:
#                 fp.write(_use_prefix('i', ArxivId.uri_namespace, doc_uri) + ' ')
#                 fp.write(' ; '.join(prefixed_has_cat + ' ' + _use_prefix('c', ArxivCategory.uri_namespace, cat) for cat in cats) + '.\n')
#     # logging.info(f'Processed {i+1} entries – writing them to {dest}')
#     # graph.serialize(fp, format='turtle')
#     # dest = '/tmp/test.rdf'
#     # graph.serialize(dest, format='turtle')


def generate_rdf():
    path = arxiv_raw_metadata_locator.require()
    if path.name.endswith('.zip'):
        with zipfile.ZipFile(path) as zf:
            with zf.open('arxiv-metadata-oai-snapshot.json') as fp:
                _generate_rdf_from_io(fp)
    else:
        with open(path) as fp:
            _generate_rdf_from_io(fp)


def main():
    loader = config_loader.ConfigLoader()
    argparser = argparse.ArgumentParser(parents=[loader.argparser])
    argparser.add_argument('command', choices=['generate-rdf', 'load-rdf'],
                           help='use "generate-rdf" to generate the RDF and "load-rdf" to load it')
    ns = argparser.parse_args()
    loader.load_from_namespace(ns)
    match ns.command:
        case 'generate-rdf':
            generate_rdf()
        case 'load-rdf':
            ...


if __name__ == '__main__':
    main()
