import spotterbase.corpora.arxiv
import spotterbase.rdf.vocab as vocab
from spotterbase.rdf.base import NameSpace, Object, Uri, Literal

NAMESPACES: list[NameSpace] = [
    vocab.RDF.NS,
    vocab.RDFS.NS,
    vocab.DCTERMS.NS,
    vocab.XSD.NS,
    vocab.OA.NS,

    spotterbase.corpora.arxiv.ArxivUris.arxiv_cat,
    spotterbase.corpora.arxiv.ArxivUris.arxiv_id,
]


def _get_prefixes(ns_list: list[NameSpace]):
    used_prefixes: set[str] = set()
    lines = []
    for ns in ns_list:
        if not ns.prefix:
            continue
        assert ns.prefix not in used_prefixes
        used_prefixes.add(ns.prefix)
        lines.append(format(ns, 'sparql'))
    return '\n'.join(lines) + '\n'


PREFIXES = _get_prefixes(NAMESPACES)


def json_binding_to_object(d: dict[str, str]) -> Object:
    match d['type']:
        case 'uri':
            return Uri(d['value'])
        case 'literal':
            if 'xml:lang' in d:
                return Literal(d['value'], vocab.RDF.langString, d['xml:lang'])
            else:
                return Literal(d['value'], vocab.XSD.string)
        case 'typed-literal':
            # TODO: somewhere creating specialized literals from corpora types.
            return Literal(d['value'], Uri(d['datatype']))
        case other:
            raise Exception(f'Unsupported type {other}')
