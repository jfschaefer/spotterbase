import json

from spotterbase.model_core import SB_JSONLD_CONTEXT
from spotterbase.model_core.sb import SB_CONTEXT_FILE


def _write_to_file():
    with open(SB_CONTEXT_FILE, 'w') as fp:
        json.dump({'@context': SB_JSONLD_CONTEXT.export_to_json()}, fp, indent=4)
        fp.write('\n')


if __name__ == '__main__':
    _write_to_file()
