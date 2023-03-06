import json
import logging

from spotterbase import config_loader
from spotterbase.annotations.concepts import ANNOTATION_CONCEPT_RESOLVER
from spotterbase.annotations.target import FragmentTarget, populate_standard_selectors
from spotterbase.concept_graphs.concept_loading import load_all_concepts_from_endpoint
from spotterbase.concept_graphs.jsonld_support import JsonLdConceptConverter
from spotterbase.concept_graphs.oa_support import OA_JSONLD_CONTEXT
from spotterbase.concept_graphs.sb_support import SB_JSONLD_CONTEXT
from spotterbase.concept_graphs.sparql_populate import Populator
from spotterbase.sparql.endpoint import RdflibEndpoint
from spotterbase.utils.logutils import ProgressLogger

logger = logging.getLogger(__name__)


def main():
    rdf_file = config_loader.ConfigPath('--file', 'the RDF file', required=True)
    jsonld_file = config_loader.ConfigPath('--output', 'the resulting .jsonld file', default='output.jsonld')

    config_loader.auto()

    endpoint = RdflibEndpoint()
    logger.info(f'Loading data from {rdf_file.value}')
    endpoint.graph.parse(rdf_file.value)
    logger.info(f'Loaded {len(endpoint.graph)} triples')

    populator = Populator(concept_resolver=ANNOTATION_CONCEPT_RESOLVER,
                          endpoint=endpoint,
                          special_populators={
                              FragmentTarget: [populate_standard_selectors]
                          })

    concepts = load_all_concepts_from_endpoint(endpoint, populator)
    logger.info('Determined potential concepts URIs')

    converter = JsonLdConceptConverter(
        contexts=[OA_JSONLD_CONTEXT, SB_JSONLD_CONTEXT],
        concept_resolver=ANNOTATION_CONCEPT_RESOLVER,
    )

    progress_logger = ProgressLogger(logger, 'Status update: Processed {progress} concepts')

    logger.info('Loading concepts and converting them to JSON-LD (this may take a while)')
    results: list = []
    for i, concept in enumerate(concepts):
        progress_logger.update(i)
        results.append(converter.concept_to_json_ld(concept))

    file = jsonld_file.value
    assert file is not None
    logger.info(f'Writing {len(results)} concepts to {file}')
    with open(file, 'w') as fp:
        json.dump(results, fp, indent=4)


if __name__ == '__main__':
    main()
