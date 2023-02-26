from spotterbase.concept_graphs.concept_graph import PredInfo
from spotterbase.concept_graphs.jsonld_support import JsonLdContext
from spotterbase.rdf.vocab import RDF, XSD
from spotterbase.sb_vocab import SB


class SB_PRED:
    # general-purpose
    val = PredInfo(RDF.value, json_ld_term='val')
    vals = PredInfo(RDF.value, json_ld_term='vals', is_rdf_list=True)
    contains = PredInfo(SB.contains, json_ld_term='contains')
    belongsTo = PredInfo(SB.belongsTo, json_ld_term='belongsTO')

    # selectors:
    endPath = PredInfo(SB.endPath, json_ld_term='endPath', literal_type=XSD.string)
    startPath = PredInfo(SB.startPath, json_ld_term='startPath', literal_type=XSD.string)
    spotterVersion = PredInfo(SB.spotterVersion, json_ld_term='spotterVersion', literal_type=XSD.string)
    withSpotter = PredInfo(SB.withSpotter, json_ld_term='withSpotter')


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
