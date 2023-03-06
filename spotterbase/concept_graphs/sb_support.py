import json
from pathlib import Path

from spotterbase.concept_graphs.concept_graph import PredInfo
from spotterbase.concept_graphs.jsonld_support import JsonLdContext
from spotterbase.rdf.vocab import RDF, XSD, RDFS
from spotterbase.sb_vocab import SB
from spotterbase.utils.resources import RESOURCES_DIR


class SB_PRED:
    # general-purpose
    val = PredInfo(RDF.value, json_ld_term='val', json_ld_type_is_id=True)
    vals = PredInfo(RDF.value, json_ld_term='vals', is_rdf_list=True, json_ld_type_is_id=True)
    belongsTo = PredInfo(SB.belongsTo, json_ld_term='belongsTo', json_ld_type_is_id=True)
    belongsTo_Rev = PredInfo(SB.belongsTo, json_ld_term='belongsTo_Rev', json_ld_type_is_id=True, is_reversed=True)
    contains = PredInfo(SB.contains, json_ld_term='contains', json_ld_type_is_id=True)
    comment = PredInfo(RDFS.comment, json_ld_term='comment', literal_type=XSD.string)

    # selectors:
    endPath = PredInfo(SB.endPath, json_ld_term='endPath', literal_type=XSD.string)
    startPath = PredInfo(SB.startPath, json_ld_term='startPath', literal_type=XSD.string)
    spotterVersion = PredInfo(SB.spotterVersion, json_ld_term='spotterVersion', literal_type=XSD.string)
    withSpotter = PredInfo(SB.withSpotter, json_ld_term='withSpotter', json_ld_type_is_id=True)


SB_JSONLD_CONTEXT: JsonLdContext = JsonLdContext(
    uri=None,
    namespaces=[SB.NS],
    pred_infos=list(p_info for p_info in SB_PRED.__dict__.values() if isinstance(p_info, PredInfo)),
    terms=[
        ('FragmentTarget', SB.FragmentTarget),
        ('ListSelector', SB.ListSelector),
        ('PathSelector', SB.PathSelector),
        ('OffsetSelector', SB.OffsetSelector),
        ('SimpleTagBody', SB.SimpleTagBody)
    ]
)

SB_CONTEXT_FILE: Path = RESOURCES_DIR / 'sb-context.jsonld'


def _write_to_file():
    with open(SB_CONTEXT_FILE, 'w') as fp:
        json.dump({'@context': SB_JSONLD_CONTEXT.export_to_json()}, fp, indent=4)
        fp.write('\n')


if __name__ == '__main__':
    _write_to_file()
