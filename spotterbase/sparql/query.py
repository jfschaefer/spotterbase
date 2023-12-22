from collections import defaultdict

import spotterbase.rdf.vocab as vocab
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.literal import Literal
from spotterbase.rdf.types import Object
from spotterbase.rdf.uri import Uri


def json_binding_to_object(d: dict[str, str], bnode_map: defaultdict[str, BlankNode]) -> Object:
    match d['type']:
        case 'uri':
            return Uri(d['value'])
        case 'literal' | 'typed-literal':
            if 'xml:lang' in d:
                return Literal(d['value'], vocab.RDF.langString, d['xml:lang'])
            elif 'datatype' in d:
                return Literal(d['value'], Uri(d['datatype']))
            else:
                return Literal(d['value'], vocab.XSD.string)
        case 'bnode':
            return bnode_map[d['value']]
        case other:
            raise Exception(f'Unsupported type {other} in entry {d}')
