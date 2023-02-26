from __future__ import annotations

from typing import Optional, Any

from spotterbase.concept_graphs.concept_graph import PredInfo, Concept, ConceptInfo, AttrInfo
from spotterbase.concept_graphs.concept_resolver import ConceptResolver
from spotterbase.rdf.uri import Uri, NameSpace


class _NodeTerms:
    def __init__(self):
        self.term_to_uri: dict[str, Uri] = {}
        self.uri_to_term: dict[Uri, str] = {}

    def get_uri(self, term: str) -> Uri:
        return self.term_to_uri[term]

    def get_term(self, uri: Uri) -> str:
        return self.uri_to_term[uri]

    def has_uri(self, uri: Uri) -> bool:
        return uri in self.uri_to_term

    def has_term(self, term: str) -> bool:
        return term in self.term_to_uri

    def add(self, term: str, uri: Uri):
        assert term not in self.term_to_uri or self.term_to_uri[term] == uri, f'{term!r} already exists'
        assert uri not in self.uri_to_term or self.uri_to_term[uri] == term, f'{uri} already has a term'
        self.term_to_uri[term] = uri
        self.uri_to_term[uri] = term


class JsonLdContext:
    """ This is a very crude implementation supporting only the necessary subset """

    def __init__(self, uri: Optional[Uri], namespaces: list[NameSpace], pred_infos: list[PredInfo],
                 terms: list[tuple[str, Uri]]):
        self.uri: Optional[Uri] = uri

        self.namespaces: dict[str, NameSpace] = {}
        for ns in namespaces:
            if ns.prefix is None:
                continue
            assert ns.prefix not in self.namespaces or self.namespaces[ns.prefix] == ns, f'{ns.prefix} already exists'
            self.namespaces[ns.prefix] = ns

        self.pred_terms: dict[str, PredInfo] = {}
        for p in pred_infos:
            if p.json_ld_term is None:
                continue
            assert p.json_ld_term not in self.pred_terms or self.pred_terms[p.json_ld_term] == p,\
                f'{p.json_ld_term} already exists'
            self.pred_terms[p.json_ld_term] = p

        self.obj_terms: _NodeTerms = _NodeTerms()
        for a, u in terms:
            self.obj_terms.add(a, u)


class JsonLdConceptConverter:
    def __init__(self, contexts: list[JsonLdContext], concept_resolver: ConceptResolver):
        self._contexts: list[JsonLdContext] = contexts
        self._merged_context: JsonLdContext = JsonLdContext(
            uri=None,
            namespaces=list(set(ns for ctx in contexts for ns in ctx.namespaces.values())),
            pred_infos=[pinfo for ctx in contexts for pinfo in ctx.pred_terms.values()],
            terms=[term for ctx in contexts for term in ctx.obj_terms.term_to_uri.items()]
        )
        self.concept_resolver: ConceptResolver = concept_resolver

    def format_uri(self, uri: Uri) -> str:
        if uri in self._merged_context.obj_terms.uri_to_term:
            return self._merged_context.obj_terms.uri_to_term[uri]
        else:
            return uri.full_uri()

    def uri_from_str(self, string: str) -> Uri:
        # option 1: it's a term
        if self._merged_context.obj_terms.has_term(string):
            return self._merged_context.obj_terms.get_uri(string)
        if ':' not in string:
            raise Exception(f'{string!r} does not appear to be a valid URI')
        # option 2: it uses a prefix
        prefix = string.split(':')[0] + ':'
        if prefix in self._merged_context.namespaces:
            return self._merged_context.namespaces[prefix][string[len(prefix):]]
        # option 3: it's the correct URI already
        return Uri(string)

    def json_ld_to_concept(self, json_ld, expect_non_root_concept: bool = False) -> Concept:
        if not isinstance(json_ld, dict):
            raise Exception(f'Expected dictionary (JSON object), not {type(json_ld)}')
        if 'type' not in json_ld:
            raise Exception('No type information in json_ld object')
        type_ = self.uri_from_str(json_ld['type'])
        if type_ not in self.concept_resolver:
            raise Exception(f'Unknown concept {type_}')
        concept = self.concept_resolver[type_]()
        c_info: ConceptInfo = concept.concept_info

        if concept.concept_info.is_root_concept:
            if expect_non_root_concept:
                raise Exception(f'Expected non-root concept, found {type(concept)} (URI: {type_})')
            assert 'id' in json_ld, 'No id provided for root concept'
        if 'id' in json_ld:
            concept.uri = self.uri_from_str(json_ld['id'])

        for key in json_ld:
            if key in {'id', 'type'}:
                continue
            a_info: AttrInfo
            if key in c_info.attrs_by_jsonld_term:
                a_info = c_info.attrs_by_jsonld_term[key]
            else:
                uri = self.uri_from_str(key)
                if uri in c_info.attrs_by_uri:
                    a_info = c_info.attrs_by_uri[uri]
                else:
                    raise Exception(f'Unknown key {key} for concept {type(concept)} ({type_})')
            setattr(concept, a_info.attr_name, self._import_json_ld_value(json_ld[key], a_info.pred_info.literal_type))

        return concept

    def _import_json_ld_value(self, value, expected_literal_type: Optional[Uri]):
        if isinstance(value, list):
            return [self._import_json_ld_value(v, expected_literal_type) for v in value]
        elif expected_literal_type:
            # TODO: properly support literals
            return value
        elif isinstance(value, dict):
            if 'type' in value:
                return self.json_ld_to_concept(value, expect_non_root_concept=True)
            if len(value) != 1 or 'id' not in value:
                raise Exception(f'Unexpected value {value} - did you forget to specify a type?')
        elif isinstance(value, str):
            return self.uri_from_str(value)
#         elif isinstance(value, int):
#             return value
        else:
            raise Exception(f'Value {value!r} has unsupported type {type(value)}')

    def concept_to_json_ld(self, concept: Concept) -> dict[str, Any]:
        result: dict[str, Any] = {'type': self.format_uri(concept.concept_info.concept_type)}
        if hasattr(concept, 'uri') and concept.uri:
            result['id'] = self.format_uri(concept.uri)

        for attr in concept.concept_info.attrs:
            p_info = attr.pred_info
            if not hasattr(concept, attr.attr_name):
                continue
            attr_val = getattr(concept, attr.attr_name)
            if attr_val is None:
                continue

            vals = attr_val if isinstance(attr_val, list) else [attr_val]

            converted: list = []
            for val in vals:
                if p_info.literal_type is not None:
                    # TODO: treat literals properly
                    converted.append(val)
                elif isinstance(val, Concept):
                    converted.append(self.concept_to_json_ld(val))
                elif isinstance(val, Uri):
                    if not p_info.json_ld_term:  # must wrap it because otherwise it would be interpreted as a literal
                        converted.append({'id': self.format_uri(val)})
                    else:
                        converted.append(self.format_uri(val))
                else:
                    raise NotImplementedError(f'Unsupported type {type(val)}')

            key = p_info.json_ld_term
            if key is None:
                key = self.format_uri(p_info.uri)
            assert key not in result
            if isinstance(attr_val, list):
                result[key] = converted
            else:
                result[key] = converted[0]

        return result
