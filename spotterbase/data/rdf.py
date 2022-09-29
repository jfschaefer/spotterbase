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


class ArxivUris:
    """ Namespaces and URIs for arXiv. Note that we are trying to use valid arxiv URLs where possible. """
    meta_graph = SB.NS['graph/arxiv-meta']

    topic_system = Uri('https://arxiv.org/category_taxonomy/')
    dataset = Uri('https://arxiv.org/')
    centi_arxiv = Uri('http://sigmathling.kwarc.info/centi-arxiv')

    arxiv_id = NameSpace('https://arxiv.org/abs/', 'arxiv:')
    arxiv_cat = NameSpace('https://arxiv.org/archive/', 'arxivcat:')


class ArXMLivUris:
    arxmliv = Uri(f'http://sigmathling.kwarc.info/arxmliv/')

    severity = arxmliv / 'severity/'
    severity_no_problem = severity / 'noProblem'
    severity_warning = severity / 'warning'
    severity_error = severity / 'error'
