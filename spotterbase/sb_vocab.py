from spotterbase.rdf.base import Vocabulary, NameSpace, Uri


class SB(Vocabulary):
    NS = NameSpace('http://sigmathling.kwarc.info/spotterbase/', 'sb:')

    # spotter info
    spotter: Uri
    spotterRun: Uri

    withSpotter: Uri
    runDate: Uri
    spotterVersion: Uri

    # selection
    docFrag: Uri

    # datasets (TODO: can this replaced with dublin core?)
    dataset: Uri
    document: Uri

    subset: Uri
    belongsTo: Uri
    basedOn: Uri

    # topics/categories (TODO: can this replaced with dublin core?)
    html5doc: Uri
    topic: Uri
    hasTopic: Uri
    subtopicOf: Uri
