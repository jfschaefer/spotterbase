from spotterbase.rdf.base import Vocabulary, NameSpace, Uri


class OM(Vocabulary):
    NS = NameSpace('http://www.ontology-of-units-of-measure.org/resource/om-2/', prefix='om:')

    Measure: Uri
    SingularUnit: Uri

    hasNumericalValue: Uri
    hasUnit: Uri
