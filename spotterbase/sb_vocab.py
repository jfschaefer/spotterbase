from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri


class SB(Vocabulary):
    NS: NameSpace = NameSpace('http://sigmathling.kwarc.info/spotterbase/', 'sb:')

    # SPOTTER INFO
    spotter: Uri
    spotterRun: Uri

    withSpotter: Uri
    runDate: Uri
    spotterVersion: Uri

    # SELECTORS
    docFrag: Uri   # TODO: Remove this

    PathSelector: Uri
    startPath: Uri
    endPath: Uri

    ListSelector: Uri
    OffsetSelector: Uri

    # BODIES
    SimpleTagBody: Uri

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
