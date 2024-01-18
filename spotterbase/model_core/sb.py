from pathlib import Path

from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri
from spotterbase.rdf.vocab import RDF, RDFS, XSD, DCTERMS
from spotterbase.records.jsonld_support import JsonLdContext
from spotterbase.records.record import PredInfo
from spotterbase.utils.resources import RESOURCES_DIR


class SB(Vocabulary):
    NS: NameSpace = NameSpace('https://ns.mathhub.info/project/sb/', 'sb:')

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
    subTagOf: Uri
    ReplacedHtmlBody: Uri

    # DATASETS (TODO: can this replaced with dublin core?)
    Corpus: Uri
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

    # different value literals
    html_val = PredInfo(RDF.value, json_ld_term='html-value', literal_type=RDF.HTML)

    # selectors:
    endPath = PredInfo(SB.endPath, json_ld_term='endPath', literal_type=XSD.string)
    startPath = PredInfo(SB.startPath, json_ld_term='startPath', literal_type=XSD.string)
    spotterVersion = PredInfo(SB.spotterVersion, json_ld_term='spotterVersion', literal_type=XSD.string)
    withSpotter = PredInfo(SB.withSpotter, json_ld_term='withSpotter', json_ld_type_is_id=True)

    # corpora
    license = PredInfo(DCTERMS.license, json_ld_term='license', json_ld_type_is_id=True)
    title = PredInfo(DCTERMS.title, json_ld_term='title', json_ld_type_is_id=True)
    year = PredInfo(DCTERMS.date, json_ld_term='year', literal_type=XSD.gYear)
    isBasedOn = PredInfo(SB.isBasedOn, json_ld_term='isBasedOn', json_ld_type_is_id=True)

    # other
    subTagOf = PredInfo(SB.subTagOf, json_ld_term='subTagOf', json_ld_type_is_id=True)


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
        ('MultiTagBody', SB.MultiTagBody),
        ('SpotterRun', SB.SpotterRun),
        ('TagSet', SB.TagSet),
        ('Tag', SB.Tag),
    ]
)
SB_CONTEXT_FILE: Path = RESOURCES_DIR / 'sb-context.jsonld'
