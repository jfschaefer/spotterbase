import json
from pathlib import Path

from spotterbase.records.record import PredInfo
from spotterbase.records.jsonld_support import JsonLdContext
from spotterbase.rdf.uri import Vocabulary, NameSpace, Uri
from spotterbase.anno_core.sb import SB
from spotterbase.utils.resources import RESOURCES_DIR


class SBX(Vocabulary):
    NS: NameSpace = NameSpace(SB.NS.uri / 'ext/', prefix='anno_extra:')

    Identifier: Uri
    IdentifierOccurrence: Uri
    IdentifierDeclaration: Uri

    occurrenceOf: Uri
    hasPolarity: Uri
    declares: Uri


class SBX_PRED:
    occurrenceOf = PredInfo(SBX.occurrenceOf, json_ld_term='occurrenceOf', json_ld_type_is_id=True)
    hasPolarity = PredInfo(SBX.hasPolarity, json_ld_term='hasPolarity', json_ld_type_is_id=True)
    declares = PredInfo(SBX.declares, json_ld_term='declares', json_ld_type_is_id=True)


SBX_JSONLD_CONTEXT: JsonLdContext = JsonLdContext(
    uri=None,
    namespaces=[SBX.NS],
    pred_infos=list(p_info for p_info in SBX_PRED.__dict__.values() if isinstance(p_info, PredInfo)),
    terms=[
        ('Identifier', SBX.Identifier),
        ('IdentifierOccurrence', SBX.IdentifierOccurrence),
        ('IdentifierDeclaration', SBX.IdentifierDeclaration),
    ]
)


SBX_CONTEXT_FILE: Path = RESOURCES_DIR / 'anno_extra-context.jsonld'


def _write_to_file():
    with open(SBX_CONTEXT_FILE, 'w') as fp:
        json.dump({'@context': SBX_JSONLD_CONTEXT.export_to_json()}, fp, indent=4)
        fp.write('\n')


if __name__ == '__main__':
    _write_to_file()
