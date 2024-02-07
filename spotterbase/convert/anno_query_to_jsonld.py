import json
from typing import Iterator

from spotterbase.rdf import Uri
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.records.sparql_populate import Populator
from spotterbase.sparql.sb_sparql import get_work_endpoint
from spotterbase.utils.config_loader import ConfigPath, auto


def main():
    DOC_QUERY_PATH = ConfigPath(
        '--anno-query',
        'Path to a file with a SPARQL query for annotations to be processed (annotation URI in ?anno)',
        required=True,
    )

    OUTPATH = ConfigPath('--output', 'the resulting .jsonld file', default='output.jsonld')

    auto()

    endpoint = get_work_endpoint()
    populator = Populator(endpoint=endpoint, chunk_size=50)

    def uri_iterator() -> Iterator[Uri]:
        query_path = DOC_QUERY_PATH.value
        assert query_path
        response = endpoint.query(query_path.read_text())
        for row in response:
            uri = row['anno']
            assert isinstance(uri, Uri)
            yield uri

    converter = JsonLdRecordConverter.default()
    results = [converter.record_to_json_ld(record) for record in populator.get_records(uris=uri_iterator())]

    outpath = OUTPATH.value
    assert outpath
    with outpath.open('w') as fp:
        json.dump(results, fp, indent=4)


if __name__ == '__main__':
    main()
