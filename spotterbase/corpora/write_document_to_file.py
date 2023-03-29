import logging
import sys

from spotterbase.utils.config_loader import ConfigLoader
from spotterbase.corpora.resolver import Resolver
from spotterbase.rdf.uri import Uri


logger = logging.getLogger(__name__)


def main():
    config_loader = ConfigLoader()
    config_loader.argparser.add_argument('uri')
    config_loader.argparser.add_argument('filename')
    args = config_loader.load_from_args()
    uri = Uri(args.uri)
    document = Resolver.get_document(uri)
    if document is None:
        logger.error(f'Failed to resolve document {uri}')
        sys.exit(1)
    with open(args.filename, 'w') as outfp:
        with document.open('r') as infp:
            outfp.write(infp.read())
    logger.info(f'Successfully wrote {uri} to {args.filename}')


if __name__ == '__main__':
    main()
