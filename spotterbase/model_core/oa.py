from spotterbase.records.record import PredInfo
from spotterbase.records.jsonld_support import JsonLdContext
from spotterbase.rdf.uri import Uri, Vocabulary, NameSpace
from spotterbase.rdf.vocab import DCTerms, XSD, DC, RDF, RDFS, OWL, AS


class OA(Vocabulary):
    """ Generated from http://www.w3.org/ns/oa.ttl """

    NS = NameSpace(Uri('http://www.w3.org/ns/oa#'), prefix='oa:')

    # PROPERTIES
    annotationService: Uri
    bodyValue: Uri
    cachedSource: Uri
    canonical: Uri
    end: Uri
    exact: Uri
    hasBody: Uri
    hasEndSelector: Uri
    hasPurpose: Uri
    hasScope: Uri
    hasSelector: Uri
    hasSource: Uri
    hasStartSelector: Uri
    hasState: Uri
    hasTarget: Uri
    motivatedBy: Uri
    prefix: Uri
    processingLanguage: Uri
    refinedBy: Uri
    renderedVia: Uri
    sourceDate: Uri
    sourceDateEnd: Uri
    sourceDateStart: Uri
    start: Uri
    styleClass: Uri
    styledBy: Uri
    suffix: Uri
    textDirection: Uri
    via: Uri

    # CLASSES
    Annotation: Uri
    Choice: Uri
    CssSelector: Uri
    CssStyle: Uri
    DataPositionSelector: Uri
    Direction: Uri
    FragmentSelector: Uri
    HttpRequestState: Uri
    Motivation: Uri
    RangeSelector: Uri
    ResourceSelection: Uri
    Selector: Uri
    SpecificResource: Uri
    State: Uri
    Style: Uri
    SvgSelector: Uri
    TextPositionSelector: Uri
    TextQuoteSelector: Uri
    TextualBody: Uri
    TimeState: Uri
    XPathSelector: Uri

    # OTHER
    PreferContainedDescriptions: Uri
    PreferContainedIRIs: Uri
    assessing: Uri
    bookmarking: Uri
    classifying: Uri
    commenting: Uri
    describing: Uri
    editing: Uri
    highlighting: Uri
    identifying: Uri
    linking: Uri
    ltrDirection: Uri
    moderating: Uri
    questioning: Uri
    replying: Uri
    rtlDirection: Uri
    tagging: Uri


class OA_PRED:
    # Predicates that are part of OA or its recommendations
    # In other words, the predicates that are part of anno.jsonld
    body = PredInfo(OA.hasBody, json_ld_term='body', json_ld_type_is_id=True)
    created = PredInfo(DCTerms.created, json_ld_term='created', literal_type=XSD.dateTime)
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
