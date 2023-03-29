import json
from pathlib import Path

from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri
from spotterbase.rdf.vocab import RDF, RDFS, XSD
from spotterbase.records.jsonld_support import JsonLdContext
from spotterbase.records.record import PredInfo
from spotterbase.utils.resources import RESOURCES_DIR


class SB(Vocabulary):
    NS: NameSpace = NameSpace('http://sigmathling.kwarc.info/spotterbase/', 'sb:')

    # SPOTTER INFO
    SpotterRun: Uri
    withSpotter: Uri
    runDate: Uri
    spotterVersion: Uri

    # SELECTORS AND TARGETS
    FragmentTarget: Uri  # type of targets that use selectors

    PathSelector: Uri
    startPath: Uri
    endPath: Uri

    ListSelector: Uri

    OffsetSelector: Uri

    # BODIES
    SimpleTagBody: Uri
    MultiTagBody: Uri
    TagSet: Uri
    Tag: Uri

    # DATASETS (TODO: can this replaced with dublin core?)
    Dataset: Uri
    Document: Uri

    isBasedOn: Uri

    # GENERAL-PURPOSE
    isSubsetOf: Uri
    belongsTo: Uri
    contains: Uri


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
        ('SimpleTagBody', SB.SimpleTagBody),
        ('SpotterRun', SB.SpotterRun),
        ('TagSet', SB.TagSet),
        ('Tag', SB.Tag),
    ]
)
SB_CONTEXT_FILE: Path = RESOURCES_DIR / 'sb-context.jsonld'


def _write_to_file():
    with open(SB_CONTEXT_FILE, 'w') as fp:
        json.dump({'@context': SB_JSONLD_CONTEXT.export_to_json()}, fp, indent=4)
        fp.write('\n')


if __name__ == '__main__':
    _write_to_file()
