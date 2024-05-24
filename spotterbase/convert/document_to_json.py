import datetime
import json
import logging
from collections import defaultdict

import spotterbase
from spotterbase.corpora.interface import Document
from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.defaults import get_arxmliv_dnm_factory
from spotterbase.dnm_nlp.word_tokenizer import word_tokenize
from spotterbase.model_core.annotation import Annotation
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigUri, ConfigPath, ConfigFlag

logger = logging.getLogger(__name__)


class Doc2JsonConverter:
    def __init__(self, include_replaced_nodes: bool = True, skip_titles: bool = False, tokenize: bool = True):
        self.include_replaced_nodes: bool = include_replaced_nodes
        self.skip_titles: bool = skip_titles
        self.tokenize = tokenize
        self.dnm_factory = get_arxmliv_dnm_factory(
            keep_titles=not skip_titles,
        )

    def _get_meta_dict(self, document: Document) -> dict:
        return {
            'document': str(document.get_uri()),
            'converter-settings': {
                'include-replaced-nodes': self.include_replaced_nodes,
                'skip-titles': self.skip_titles,
                'tokenize': self.tokenize,
            },
            'conversion-date': datetime.datetime.now().isoformat(),
            'spotterbase-version': spotterbase.__version__,
        }

    def _process_tokenized(self, document: Document) -> dict:
        result = self._get_meta_dict(document)
        dnm = self.dnm_factory.dnm_from_document(document)

        converter = JsonLdRecordConverter.default()

        tokens: list[dict] = []
        result['tokens'] = tokens

        embedded_annos: dict[tuple[int, int], list[Annotation]] = defaultdict(list)
        for _, offsets, anno in dnm.get_meta_info().embedded_annotations:
            embedded_annos[(offsets.start, offsets.end)].append(anno)

        for word in word_tokenize(dnm, keep_as_words=[
            dnm.get_indices_from_ref_range(*offset_tuple)
            # for _, offsets, _ in dnm.get_meta_info().embedded_annotations
            for offset_tuple in embedded_annos.keys()
        ]):
            record = {
                'token': str(word),
                'start-ref': word.get_start_ref(),
                'end-ref': word.get_end_ref(),
            }

            if self.include_replaced_nodes and (word.get_start_ref(), word.get_end_ref()) in embedded_annos:
                record['annotations'] = [
                    converter.record_to_json_ld(anno)
                    for anno in embedded_annos[(word.get_start_ref(), word.get_end_ref())]
                ]
            tokens.append(record)

        return result

    def _process_untokenized(self, document: Document) -> dict:
        converter = JsonLdRecordConverter.default()
        result = self._get_meta_dict(document)
        dnm = self.dnm_factory.dnm_from_document(document)
        result['plaintext'] = str(dnm)
        result['start-refs'] = list(dnm.get_start_refs())
        result['end-refs'] = list(dnm.get_end_refs())
        if self.include_replaced_nodes:
            result['annotations'] = [
                {
                    'start-ref': offrange.start,
                    'end-ref': offrange.end,
                    'string': string,
                    'annotation': converter.record_to_json_ld(anno),
                }
                for string, offrange, anno in dnm.get_meta_info().embedded_annotations
            ]

        return result

    def process(self, document: Document) -> dict:
        if self.tokenize:
            return self._process_tokenized(document)
        else:
            return self._process_untokenized(document)


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
        self.tokenize = ConfigFlag(
            '--tokenize',
            'Return a document tokenized into works'
        )

    def create(self) -> Doc2JsonConverter:
        return Doc2JsonConverter(
            include_replaced_nodes=self.include_replaced_nodes.value,
            skip_titles=self.skip_titles.value,
            tokenize=self.tokenize.value,
        )


def main():
    document = ConfigUri('--document', 'URI of the document to be converted')
    outpath = ConfigPath('--output', 'target path')
    converter_factory = Doc2JsonConverterCmdFactory()
    config_loader.auto()
    assert document.value
    actual_doc = Resolver.get_document(document.value)
    if actual_doc is None:
        raise ValueError(f'Failed to find document {document.value} in any of the corpora')
    assert outpath.value
    with open(outpath.value, 'w') as fp:
        json.dump(converter_factory.create().process(actual_doc), fp, indent=2)
    logging.info(f'Wrote pre-processed document to {outpath.value}')


if __name__ == '__main__':
    main()
