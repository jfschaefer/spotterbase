import datetime
import json
import logging

from lxml import etree

import spotterbase
from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.defaults import get_simple_arxmliv_factory
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigUri, ConfigPath


logger = logging.getLogger(__name__)


class Doc2JsonConverter:
    def __init__(self, include_replaced_nodes: bool = True, skip_titles: bool = False, tokenize: bool = True):
        self.include_replaced_nodes: bool = include_replaced_nodes
        self.skip_titles: bool = skip_titles
        self.tokenize = tokenize
        self.dnm_factory = get_simple_arxmliv_factory(
            keep_titles=not skip_titles,
            # wrapping with spaces that they will be treated as separate words by word tokenizer
            token_prefix=' ' if tokenize else '',
            token_suffix=' ' if tokenize else '',
        )

    def process(self, document: Document) -> dict:
        result: dict = {
            'document': str(document.get_uri()),
            'converter-settings': {
                'include-replaced-nodes': self.include_replaced_nodes,
                'skip-titles': self.skip_titles,
            },
            'conversion-date': datetime.datetime.now().isoformat(),
            'spotterbase-version': spotterbase.__version__,
        }
        tokens: list[dict] = []

        dnm = self.dnm_factory.dnm_from_document(document)
        if self.tokenize:
            result['tokens'] = tokens
            for word in word_tokenize(dnm):
                record = {
                    'token': str(word),
                    'start-ref': word.get_start_ref(),
                    'end-ref': word.get_end_ref(),
                }
                # if word in {'MathNode', 'MathGroup', 'LtxCite', 'LtxRef', 'MathEquation'}
                if len(word) > 1 and word.get_start_refs()[0] == word.get_start_refs()[-1] and \
                        word.get_end_refs()[0] == word.get_end_refs()[-1]:
                    # a node was replaced with a token
                    if self.include_replaced_nodes:
                        node = word.to_dom().get_containing_node()
                        tail = node.tail
                        node.tail = None
                        record['replaced-node'] = etree.tostring(node, encoding='utf-8').decode('utf-8')
                        node.tail = tail
                tokens.append(record)
        else:
            result['plaintext'] = str(dnm)
            result['start-refs'] = list(dnm.get_start_refs())
            result['end-refs'] = list(dnm.get_end_refs())

        return result


class Doc2JsonConverterCmdFactory:
    def __init__(self):
        self.include_replaced_nodes = config_loader.ConfigFlag(
            '--include-replaced-nodes',
            'Include the replaced nodes (e.g. <math> nodes) in the output'
        )
        self.skip_titles = config_loader.ConfigFlag(
            '--skip-titles',
            'Skip titles in the document'
        )

    def create(self) -> Doc2JsonConverter:
        return Doc2JsonConverter(
            include_replaced_nodes=self.include_replaced_nodes.value,
            skip_titles=self.skip_titles.value,
            tokenize=False,
        )


def main():
    document = ConfigUri('--document', 'URI of the document to be converted')
    outpath = ConfigPath('--output', 'target path')
    converter_factory = Doc2JsonConverterCmdFactory()
    config_loader.auto()
    assert document.value
    actual_doc = Resolver.get_document(document.value)
    assert actual_doc is not None
    assert outpath.value
    with open(outpath.value, 'w') as fp:
        json.dump(converter_factory.create().process(actual_doc), fp, indent=2)
    logging.info(f'Wrote pre-processed document to {outpath.value}')


if __name__ == '__main__':
    main()