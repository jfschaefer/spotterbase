import datetime
import json

from lxml import etree

import spotterbase
from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.simple_dnm_factory import ARXMLIV_STANDARD_DNM_FACTORY
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigUri, ConfigPath


class Doc2JsonConverter:
    def __init__(self, include_replaced_nodes: bool = True):
        self.include_replaced_nodes: bool = include_replaced_nodes

    def process(self, document: Document) -> dict:
        tokens: list[dict] = []
        result: dict = {
            'document': str(document.get_uri()),
            'converter-settings': {
                'include-replaced-nodes': self.include_replaced_nodes
            },
            'conversion-date': datetime.datetime.now().isoformat(),
            'spotterbase-version': spotterbase.__version__,
            'tokens': tokens,
        }
        dnm = ARXMLIV_STANDARD_DNM_FACTORY.dnm_from_document(document)
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
                    record['replaced-node'] = etree.tostring(word.to_dom().get_containing_node(),
                                                             encoding='utf-8').decode('utf-8')
            tokens.append(record)

        return result


def main():
    document = ConfigUri('--document', 'URI of the document to be tokenized')
    outpath = ConfigPath('--output', 'Path to the tokenized document')
    config_loader.auto()
    assert document.value
    actual_doc = Resolver.get_document(document.value)
    assert actual_doc is not None
    assert outpath.value
    with open(outpath.value, 'w') as fp:
        json.dump(Doc2JsonConverter(include_replaced_nodes=True).process(actual_doc), fp, indent=2)


if __name__ == '__main__':
    main()
