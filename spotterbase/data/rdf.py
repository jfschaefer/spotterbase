from spotterbase.rdf.base import Vocabulary, NameSpace, Uri


class SB(Vocabulary):
    NS = NameSpace('http://sigmathling.kwarc.info/spotterbase/', 'sb:')

    # spotter info
    spotter: Uri
    spotterRun: Uri

    withSpotter: Uri
    runDate: Uri
    spotterVersion: Uri

    # datasets
    dataset: Uri
    document: Uri

    subset: Uri
    belongsTo: Uri
    basedOn: Uri

    # topics/categories
    html5doc: Uri
    topic: Uri
    hasTopic: Uri
    subtopicOf: Uri
