import spotterbase.rdf.vocab as vocab
from spotterbase.rdf.bnode import BlankNode, counter_factory, uuid4_factory, anonymized_uuid1_factory
from spotterbase.rdf.literal import Literal
from spotterbase.rdf.namespace_collection import NameSpaceCollection, StandardNameSpaces
from spotterbase.rdf.serializer import Serializer, FileSerializer, NTriplesSerializer, TurtleSerializer, \
    triples_to_nt_string
from spotterbase.rdf.types import Subject, Predicate, Object, Triple, TripleI
from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri, UriLike


def as_uri(uri: UriLike, namespace_collection: NameSpaceCollection = StandardNameSpaces) -> Uri:
    if isinstance(uri, str):
        return namespace_collection.uri_from_prefixed_string(uri, require_prefix_supported=False)
    return Uri(uri)
