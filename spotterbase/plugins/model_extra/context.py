import json
from pathlib import Path

from spotterbase.plugins.model_extra.declarations import DECL_JSONLD_CTX
from spotterbase.utils.resources import RESOURCES_DIR

MODEL_EXTRA_CONTEXT_FILE: Path = RESOURCES_DIR / 'sbx.jsonld'


def _write_to_file():
    with open(MODEL_EXTRA_CONTEXT_FILE, 'w') as fp:
        json.dump({'@context': DECL_JSONLD_CTX.export_to_json()}, fp, indent=4)
        fp.write('\n')


if __name__ == '__main__':
    _write_to_file()
