from spotterbase.concept_graphs.concept_graph import PredInfo
from spotterbase.concept_graphs.jsonld_support import JsonLdContext
from spotterbase.rdf.uri import Uri
from spotterbase.rdf.vocab import DCTerms, OA, XSD, DC, RDF, RDFS, OWL, AS


class OA_PRED:
    # Predicates that are part of OA or its recommendations
    # In other words, the predicates that are part of anno.jsonld
    body = PredInfo(OA.hasBody, json_ld_term='body', json_ld_type_is_id=True)
    creator = PredInfo(DCTerms.creator, json_ld_term='creator', json_ld_type_is_id=True)
    end = PredInfo(OA.end, json_ld_term='end', literal_type=XSD.nonNegativeInteger)
    label = PredInfo(RDFS.label, json_ld_term='label')
    refinedBy = PredInfo(OA.refinedBy, json_ld_term='refinedBy', json_ld_type_is_id=True)
    selector = PredInfo(OA.hasSelector, json_ld_term='selector', json_ld_type_is_id=True)
    source = PredInfo(OA.hasSource, json_ld_term='source', json_ld_type_is_id=True)
    start = PredInfo(OA.start, json_ld_term='start', literal_type=XSD.nonNegativeInteger)
    target = PredInfo(OA.hasTarget, json_ld_term='target', json_ld_type_is_id=True)


# TODO: this is not complete
OA_JSONLD_CONTEXT: JsonLdContext = JsonLdContext(
    uri=Uri('http://www.w3.org/ns/anno.jsonld'),
    namespaces=[OA.NS, DC.NS, DCTerms.NS, DC.NS, RDF.NS, RDFS.NS, XSD.NS, OWL.NS, AS.NS],
    pred_infos=list(p_info for p_info in OA_PRED.__dict__.values() if isinstance(p_info, PredInfo)),
    terms=[
        ('Annotation', OA.Annotation),
    ]
)
