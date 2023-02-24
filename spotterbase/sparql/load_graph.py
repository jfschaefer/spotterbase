import gzip
import logging
import shutil
from pathlib import Path

from spotterbase.config_loader import ConfigLoader
from spotterbase.data.locator import TmpDir
from spotterbase.rdf.uri import Uri
from spotterbase.sparql.endpoint import get_endpoint

logger = logging.getLogger(__name__)


def load_graph(rdf_file: Path):
    if not rdf_file.name.endswith('.ttl.gz'):
        raise NotImplementedError(f'Unsupported file extension: {rdf_file.name} (Only *.ttl.gz is supported)')
    # have to extract due to a bug (?) in Virtuoso
    tmp_file = TmpDir.get('extracted.ttl')
    logger.info(f'Extracting {rdf_file} into {tmp_file}')
    with open(tmp_file, 'w') as fp_out:
        with gzip.open(rdf_file, 'rt') as fp_in:
            shutil.copyfileobj(fp_in, fp_out)
    with open(tmp_file, 'r') as fp:
        first_line = fp.readline()
        if not first_line.startswith('# Graph: '):
            raise Exception(f'{rdf_file} does not start with "# Graph: <...>" comment')
        graph = Uri(first_line[len('# Graph: '):].strip())
    endpoint = get_endpoint()
    logger.info(f'Deleting {graph:<>} in endpoint')
    endpoint.post(f'CLEAR GRAPH {graph:<>}')
    logger.info(f'Loading {graph:<>} from {tmp_file}')
    endpoint.post(f'LOAD {Uri(tmp_file):<>} INTO GRAPH {graph:<>}')
    tmp_file.unlink()


def main():
    config_loader = ConfigLoader()
    config_loader.argparser.add_argument('rdffile', nargs="+")
    args = config_loader.load_from_args()
    for rdf_file in args.rdffile:
        load_graph(Path(rdf_file))
    logger.info('Done')


if __name__ == '__main__':
    main()
