from rdflib import Namespace, URIRef
from rdflib.namespace import DefinedNamespace


class SB(DefinedNamespace):
    _NS = Namespace('http://sigmathling.kwarc.info/spotterbase/')
    _warn = False

    # spotter info
    spotter: URIRef
    spotterRun: URIRef

    withSpotter: URIRef
    runDate: URIRef
    spotterVersion: URIRef

    # datasets
    dataset: URIRef
    document: URIRef

    subset: URIRef
    belongsto: URIRef
    basedOn: URIRef

    # topics/categories
    html5doc: URIRef
    topic: URIRef
    hasTopic: URIRef
    subtopicOf: URIRef


class OA(DefinedNamespace):
    _NS = Namespace('http://www.w3.org/ns/oa#')

    Annotation: URIRef

    hasBody: URIRef
    hasTarget: URIRef


class AS(DefinedNamespace):
    _NS = Namespace('http://www.w3.org/ns/activitystreams#')

    generator: URIRef


class DCTERMS(DefinedNamespace):
    _NS = Namespace('http://purl.org/dc/terms/')

    creator: URIRef