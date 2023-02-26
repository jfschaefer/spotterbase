from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri


class SB(Vocabulary):
    NS: NameSpace = NameSpace('http://sigmathling.kwarc.info/spotterbase/', 'sb:')

    # SPOTTER INFO
    SpotterRun: Uri
    withSpotter: Uri
    runDate: Uri
    spotterVersion: Uri

    # SELECTORS AND TARGETS
    FragmentTarget: Uri   # type of targets that use selectors

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
