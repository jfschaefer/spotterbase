import json
import logging

from spotterbase.utils import config_loader
from spotterbase.anno_core.record_class_resolver import ANNOTATION_RECORD_CLASS_RESOLVER
from spotterbase.anno_core.target import FragmentTarget, populate_standard_selectors
from spotterbase.records.record_loading import load_all_records_from_graph
from spotterbase.records.record_class_resolver import RecordClassResolver
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.records.oa_support import OA_JSONLD_CONTEXT
from spotterbase.anno_core.sb import SB_JSONLD_CONTEXT
from spotterbase.records.sparql_populate import Populator
from spotterbase.rdf.uri import Uri
from spotterbase.sparql.sb_sparql import get_work_endpoint, get_tmp_graph_uri
from spotterbase.anno_extra.sbx import SBX_JSONLD_CONTEXT
from spotterbase.anno_extra.record_class_resolver import SBX_RECORD_CLASS_RESOLVER
from spotterbase.utils.progress_updater import ProgressUpdater

logger = logging.getLogger(__name__)


def main():
    rdf_file = config_loader.ConfigPath('--file', 'the RDF file', required=True)
    jsonld_file = config_loader.ConfigPath('--output', 'the resulting .jsonld file', default='output.jsonld')

    config_loader.auto()

    endpoint = get_work_endpoint()
    populator = Populator(
        record_type_resolver=RecordClassResolver.merged(ANNOTATION_RECORD_CLASS_RESOLVER, SBX_RECORD_CLASS_RESOLVER),
        endpoint=endpoint,
        special_populators={FragmentTarget: [populate_standard_selectors]},
        chunk_size=50)

    graph_uri = get_tmp_graph_uri()

    try:
        endpoint.update(f'CREATE GRAPH {graph_uri:<>}')
        file = rdf_file.value
        assert file is not None
        logger.info(f'Loading data from {Uri(file)} into {graph_uri}')
        endpoint.update(f'LOAD {Uri(file):<>} INTO GRAPH {graph_uri:<>}')
        logger.info('Finished loading data')
        records = load_all_records_from_graph(endpoint, graph_uri, populator)
        logger.info('Determined potential records URIs')

        converter = JsonLdRecordConverter(
            contexts=[OA_JSONLD_CONTEXT, SB_JSONLD_CONTEXT, SBX_JSONLD_CONTEXT],
            record_type_resolver=populator.record_type_resolver,
        )

        progress_logger = ProgressUpdater('Status update: Processed {progress} records')

        logger.info('Loading records and converting them to JSON-LD (this may take a while)')
        results: list = []
        for i, record in enumerate(records):
            progress_logger.update(i)
            results.append(converter.record_to_json_ld(record))
    finally:
        logger.info(f'Dropping temporarily created graph {graph_uri}')
        endpoint.update(f'DROP GRAPH {graph_uri:<>}')

    file = jsonld_file.value
    assert file is not None
    logger.info(f'Writing {len(results)} records to {file}')
    with open(file, 'w') as fp:
        json.dump(results, fp, indent=4)


if __name__ == '__main__':
    main()
