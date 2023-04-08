import unittest

import rdflib

from spotterbase.records.record import PredInfo, AttrInfo, Record, RecordInfo, FieldKnownRecord
from spotterbase.records.record_class_resolver import RecordClassResolver
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.model_core.oa import OA_JSONLD_CONTEXT
from spotterbase.records.sparql_populate import Populator
from spotterbase.rdf.serializer import triples_to_nt_string
from spotterbase.rdf.uri import Vocabulary, NameSpace, Uri
from spotterbase.rdf.vocab import OA, XSD
from spotterbase.sparql.endpoint import RdflibEndpoint


class TestVocab(Vocabulary):
    NS = NameSpace(Uri('http://example.org/sb-test#'), prefix='sbtest:')

    edge: Uri
    edge3: Uri
    thingA: Uri
    thingB: Uri
    typeA: Uri
    typeB: Uri


class TestPredicates:
    edge: PredInfo = PredInfo(TestVocab.edge, json_ld_term='edge-in-json-ld', json_ld_type_is_id=True)
    edge2: PredInfo = PredInfo(TestVocab.edge, json_ld_term='edge2-in-json-ld', json_ld_type_is_id=True)
    edge3: PredInfo = PredInfo(TestVocab.edge3, json_ld_term='edge3-in-json-ld', literal_type=XSD.integer)


class TestRecords(unittest.TestCase):
    def test_simple(self):
        class MiniSubRecord(Record):
            record_info = RecordInfo(
                record_type=TestVocab.typeB,
                attrs=[
                    AttrInfo('thing', TestPredicates.edge2),
                    AttrInfo('numbers', TestPredicates.edge3, multi_field=True)
                ]
            )

            thing: Uri
            numbers: list[int]

        class MiniRecord(Record):
            record_info = RecordInfo(
                record_type=TestVocab.typeA,
                attrs=[AttrInfo('val', TestPredicates.edge, field_info=FieldKnownRecord(MiniSubRecord))],
                is_root_record=True,
            )

            val: MiniSubRecord

        record = MiniRecord()
        record.val = MiniSubRecord()
        record.val.thing = OA.Annotation
        record.val.numbers = [1, 5, 3]
        record.uri = TestVocab.thingA

        record_type_resolver = RecordClassResolver([MiniRecord, MiniSubRecord])

        # test json-ld conversion
        converter = JsonLdRecordConverter(contexts=[OA_JSONLD_CONTEXT], record_type_resolver=record_type_resolver)
        json_ld = converter.record_to_json_ld(record)
        self.assertEqual(json_ld, {'type': 'http://example.org/sb-test#typeA',
                                   'id': 'http://example.org/sb-test#thingA', 'edge-in-json-ld':
                                       {'type': 'http://example.org/sb-test#typeB',
                                        'edge2-in-json-ld': 'Annotation',
                                        'edge3-in-json-ld': [1, 5, 3]}
                                   })
        record_2 = converter.json_ld_to_record(json_ld)
        self.assertEqual(json_ld, converter.record_to_json_ld(record_2))

        # test rdf serialization/querying
        graph = rdflib.Graph()
        graph.parse(data=triples_to_nt_string(record.to_triples()), format='nt')
        endpoint = RdflibEndpoint(graph)
        populator = Populator(record_type_resolver=record_type_resolver, endpoint=endpoint)
        records = list(populator.get_records(iter((record.uri,))))
        self.assertEqual(len(records), 1)
        new_record = records[0]
        self.assertIsInstance(new_record, MiniRecord)
        assert isinstance(new_record, MiniRecord)   # make mypy happy too
        self.assertEqual(new_record.uri, record.uri)
        self.assertEqual(new_record.val.thing, OA.Annotation)
        self.assertEqual(new_record.val.numbers, [1, 5, 3])
