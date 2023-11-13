import functools
import json
import logging

from spotterbase.corpora.resolver import Resolver
from spotterbase.data import fast_json
from spotterbase.model_core.oa import OA_JSONLD_CONTEXT
from spotterbase.model_core.record_class_resolver import ANNOTATION_RECORD_CLASS_RESOLVER
from spotterbase.model_core.sb import SB_JSONLD_CONTEXT
from spotterbase.model_core.selector import PathSelector, OffsetSelector
from spotterbase.model_core.target import FragmentTarget
from spotterbase.rdf import Uri
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.records.record import Record
from spotterbase.selectors.offset_converter import OffsetConverter
from spotterbase.selectors.selector_converter import SelectorConverter
from spotterbase.utils import config_loader
from spotterbase.utils.config_loader import ConfigPath

logger = logging.getLogger(__name__)


@functools.lru_cache(5)   # usually, targets are sorted by document -> at least the "current" document should be cached
def get_selector_converter(document_uri: Uri) -> SelectorConverter:
    document = Resolver.get_document(document_uri)
    if not document:
        raise Exception(f'Could not find document {document_uri}')
    dom = document.get_html_tree(cached=True).getroot()
    return SelectorConverter(
        document_uri=document_uri,
        dom=dom,
        offset_converter=OffsetConverter(dom),
    )


def normalize_target(target: FragmentTarget):
    converter = get_selector_converter(target.source)
    selector_lookup: dict[type[Record], Record] = {}
    for selector in target.selectors:
        if type(selector) in selector_lookup:
            logger.warning(f'Found two selectors of type {type(selector)}')
        selector_lookup[type(selector)] = selector

    if PathSelector in selector_lookup:
        main_selector = selector_lookup[PathSelector]
        assert isinstance(main_selector, PathSelector)   # make the type checker happy
        dom_range, subranges = converter.selector_to_dom(main_selector)
    elif OffsetSelector in selector_lookup:
        main_selector = selector_lookup[OffsetSelector]
        assert isinstance(main_selector, OffsetSelector)
        dom_range, subranges = converter.selector_to_dom(main_selector)
    else:
        raise Exception(f'target {target.uri} has no supported selector')

    # here: opportunity to normalize dom_range, subranges

    target.selectors = converter.dom_to_selectors(dom_range, subranges)


def process(input_json_records: list) -> list:
    result: list = []

    converter = JsonLdRecordConverter(
        contexts=[OA_JSONLD_CONTEXT, SB_JSONLD_CONTEXT],
        record_type_resolver=ANNOTATION_RECORD_CLASS_RESOLVER,
    )

    for obj in input_json_records:
        is_frag_target: bool = True
        if not isinstance(obj, dict):
            is_frag_target = False
            logger.warning(f'Espected JSON object, found {type(obj)}')
        if 'type' not in obj:
            is_frag_target = False
            logger.warning('Found entry without type')
        if obj['type'] != 'FragmentTarget':
            is_frag_target = False

        if is_frag_target:
            target = converter.json_ld_to_record(obj)
            assert isinstance(target, FragmentTarget)
            normalize_target(target)
            result.append(converter.record_to_json_ld(target))
        else:
            result.append(obj)

    return result


def main():
    inpath = ConfigPath('--input', 'file with JSON annotations to be normalized', required=True)
    outpath = ConfigPath('--output', 'output file', required=True)
    config_loader.auto()

    assert inpath.value is not None
    with open(inpath.value, 'rb') as infile:
        input_json_records = fast_json.load(infile)
    output_json_records = process(input_json_records)
    assert outpath.value is not None
    with open(outpath.value, 'w') as outfile:
        json.dump(output_json_records, outfile, indent=2)


if __name__ == '__main__':
    main()
