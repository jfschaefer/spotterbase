from __future__ import annotations

from typing import Optional, Any, Iterator

from spotterbase.records.record import PredInfo, Record, RecordInfo, AttrInfo
from spotterbase.records.record_class_resolver import RecordClassResolver, DefaultRecordClassResolver
from spotterbase.rdf.literal import Literal
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
            assert p.json_ld_term not in self.pred_terms or self.pred_terms[p.json_ld_term] == p, \
                f'{p.json_ld_term} already exists'
            self.pred_terms[p.json_ld_term] = p

        self.obj_terms: _NodeTerms = _NodeTerms()
        for a, u in terms:
            self.obj_terms.add(a, u)

    def export_to_json(self) -> dict:
        result: dict[str, str | dict[str, str]] = {}
        for prefix, namespace in self.namespaces.items():
            result[prefix[:-1]] = format(namespace.uri, 'plain')

        for term, p_info in self.pred_terms.items():
            sub_result = {}
            sub_result['@id'] = format(p_info.uri, 'plain')
            if p_info.json_ld_type_is_id:
                sub_result['@type'] = '@id'
            if p_info.is_rdf_list:
                sub_result['@container'] = '@list'
            if p_info.literal_type is not None:
                assert '@type' not in sub_result
                sub_result['@type'] = format(p_info.literal_type, 'plain')

            if p_info.is_reversed:
                result[term + '_unreversed'] = sub_result
                result[term] = {'@reverse': term + '_unreversed'}
            else:
                result[term] = sub_result

        for term, uri in self.obj_terms.term_to_uri.items():
            result[term] = format(uri, 'plain')
        return result


class JsonLdRecordConverter:
    def __init__(self, contexts: list[JsonLdContext], record_type_resolver: RecordClassResolver):
        self._contexts: list[JsonLdContext] = contexts
        self._merged_context: JsonLdContext = JsonLdContext(
            uri=None,
            namespaces=list(set(ns for ctx in contexts for ns in ctx.namespaces.values())),
            pred_infos=[pinfo for ctx in contexts for pinfo in ctx.pred_terms.values()],
            terms=[term for ctx in contexts for term in ctx.obj_terms.term_to_uri.items()]
        )
        self.record_type_resolver: RecordClassResolver = record_type_resolver

    @classmethod
    def default(cls) -> JsonLdRecordConverter:
        return DefaultContexts.get_converter()

    def format_uri(self, uri: Uri) -> str:
        # TODO: should we use namespaces?
        if uri in self._merged_context.obj_terms.uri_to_term:
            return self._merged_context.obj_terms.uri_to_term[uri]
        else:
            return str(uri)

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

    def json_ld_to_record(self, json_ld, expect_non_root_record: bool = False) -> Record:
        if not isinstance(json_ld, dict):
            raise Exception(f'Expected dictionary (JSON object), not {type(json_ld)}')
        if 'type' not in json_ld:
            raise Exception('No type information in json_ld object')
        type_ = self.uri_from_str(json_ld['type'])
        if type_ not in self.record_type_resolver:
            raise Exception(f'Unknown record type {type_}')
        record = self.record_type_resolver[type_]()
        c_info: RecordInfo = record.record_info

        if record.record_info.is_root_record:
            if expect_non_root_record:
                raise Exception(f'Expected non-root record, found {type(record)} (URI: {type_})')
            assert 'id' in json_ld, 'No id provided for root record'
        if 'id' in json_ld:
            record.uri = self.uri_from_str(json_ld['id'])

        for key in json_ld:
            if key in {'id', 'type', '@context'}:
                continue
            a_info: AttrInfo
            if key in c_info.attrs_by_jsonld_term:
                a_info = c_info.attrs_by_jsonld_term[key]
            else:
                uri = self.uri_from_str(key)
                if uri in c_info.attrs_by_uri:
                    a_info = c_info.attrs_by_uri[uri]
                else:
                    raise Exception(f'Unknown key {key} for record {type(record)} ({type_})')
            v = self._import_json_ld_value(json_ld[key], a_info.literal_type,
                                           expected_id=a_info.pred_info.json_ld_type_is_id)
            setattr(record, a_info.attr_name, v)

        return record

    def _import_json_ld_value(self, value, expected_literal_type: Optional[Uri], expected_id: bool = False):
        if isinstance(value, list):
            return [self._import_json_ld_value(v, expected_literal_type, expected_id) for v in value]
        elif expected_literal_type:
            assert not expected_id
            if isinstance(value, str):
                literal = Literal(value, expected_literal_type)
            else:
                literal = Literal.from_py_val(value, datatype=expected_literal_type)
            return literal.to_py_val()
        elif isinstance(value, dict):
            if 'type' in value:
                return self.json_ld_to_record(value, expect_non_root_record=True)
            if len(value) != 1 or 'id' not in value:
                raise Exception(f'Unexpected value {value} - did you forget to specify a type?')
        elif isinstance(value, str):
            if not expected_id:
                raise Exception(f'Expected neither a string literal nor an identifier, but got {value!r}')
            return self.uri_from_str(value)
        else:
            raise Exception(f'Value {value!r} has unsupported type {type(value)}')

    def record_to_json_ld(self, record: Record) -> dict[str, Any]:
        result: dict[str, Any] = {'type': self.format_uri(record.record_info.record_type)}
        if hasattr(record, 'uri') and record.uri:
            result['id'] = self.format_uri(record.uri)

        for attr in record.record_info.attrs:
            p_info = attr.pred_info
            if not hasattr(record, attr.attr_name):
                continue
            attr_val = getattr(record, attr.attr_name)
            if attr_val is None:
                continue

            vals = attr_val if isinstance(attr_val, list) else [attr_val]

            converted: list = []
            for val in vals:
                if p_info.literal_type is not None:
                    if isinstance(val, int) or isinstance(val, str) or isinstance(val, float):
                        # TODO: this is not very proper.
                        # Note that we cannot simply use the literal type as an indicated because
                        # values other than XSD.integer may still be reasonably represented as an integer in
                        # JSON-LD (as long as the literal type is explicitly set (e.g. in the context))
                        converted.append(val)
                    else:
                        converted.append(Literal.from_py_val(val, p_info.literal_type).string)
                elif isinstance(val, Record):
                    converted.append(self.record_to_json_ld(val))
                elif isinstance(val, Uri):
                    if not p_info.json_ld_type_is_id:
                        # must wrap it because otherwise it would be interpreted as a literal
                        converted.append({'id': self.format_uri(val)})
                    else:
                        converted.append(self.format_uri(val))
                else:
                    if not p_info.json_ld_type_is_id:
                        # TODO: treat literals properly
                        converted.append(val)

            key = p_info.json_ld_term
            if key is None:
                key = self.format_uri(p_info.uri)
            assert key not in result
            if isinstance(attr_val, list):
                result[key] = converted
            else:
                result[key] = converted[0]

        return result


class DefaultContexts:
    _contexts: list[JsonLdContext] = []
    _converter: Optional[JsonLdRecordConverter] = None

    @classmethod
    def get(cls) -> list[JsonLdContext]:
        return cls._contexts

    @classmethod
    def __iter__(cls) -> Iterator[JsonLdContext]:
        return iter(cls._contexts)

    @classmethod
    def append(cls, ctx: JsonLdContext):
        cls._contexts.append(ctx)

    @classmethod
    def get_converter(cls, record_class_resolver: Optional[RecordClassResolver] = None) -> JsonLdRecordConverter:
        if record_class_resolver is None:
            if cls._converter is None:
                cls._converter = JsonLdRecordConverter(
                    contexts=cls._contexts,
                    record_type_resolver=DefaultRecordClassResolver,
                )
            return cls._converter
        else:
            return JsonLdRecordConverter(
                contexts=cls._contexts,
                record_type_resolver=record_class_resolver,
            )
