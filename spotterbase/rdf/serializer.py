import abc
from collections import OrderedDict, defaultdict
from typing import Iterable, TextIO

from spotterbase.rdf.base import Triple, Uri, Object, NameSpace, Subject, BlankNode, Predicate


class Serializer(abc.ABC):
    def add(self, triple: Triple):
        raise NotImplementedError()

    def add_from_iterable(self, triples: Iterable[Triple]):
        for triple in triples:
            self.add(triple)

    def flush(self):
        pass


class TurtleSerializer(Serializer):
    def __init__(self, fp: TextIO, buffer_size: int = 1000):
        self.fp = fp
        self.max_buffer_size = buffer_size
        self.cur_buffer_size = 0
        self.buffer: OrderedDict[Subject, list[tuple[Predicate, Object]]] = OrderedDict()
        self.used_prefixes: dict[str, str] = {}

    def add(self, triple: Triple):
        if triple.s in self.buffer:
            self.buffer[triple.s].append((triple.p, triple.o))
            self.buffer.move_to_end(triple.s)
        else:
            self.buffer[triple.s] = [(triple.p, triple.o)]
        self.cur_buffer_size += 1
        if self.cur_buffer_size >= self.max_buffer_size:
            self._write_one_from_buffer()

    def _write_one_from_buffer(self):
        subject, pairs = self.buffer.popitem(last=False)
        self.cur_buffer_size -= len(pairs)

        self._require_prefix(subject.namespace)
        prop_to_obj = defaultdict(list)
        for prop, obj in pairs:
            self._require_prefix(prop.namespace)
            self._require_prefix(obj.namespace)
            prop_to_obj[prop].append(obj)

        self._write_node(subject)
        first_prop = True
        for prop, objs in prop_to_obj.items():
            if first_prop:
                self.fp.write(' ')
                first_prop = False
            else:
                self.fp.write(' ;\n  ')
            self._write_node(prop)
            first_obj = True
            for obj in objs:
                if first_obj:
                    self.fp.write(' ')
                    first_obj = False
                else:
                    self.fp.write(',\n    ')
                self._write_node(obj)
        self.fp.write('\n')

    def _write_node(self, node: Subject | Predicate | Object):
        match node:
            case Uri():
                self.fp.write(node.format(with_angular_brackets=True, allow_prefixed=True))
            case BlankNode():
                self.fp.write(f'_:{node.value}')
            case _:
                raise NotImplementedError(f'Unsupported node type {type(node)}')

    def _require_prefix(self, ns: NameSpace):
        if not ns.prefix:
            return
        if ns.prefix in self.used_prefixes:
            if self.used_prefixes[ns.prefix] != str(ns.uri):
                raise Exception(f'Prefix "{ns.prefix}" used for two different namespaces: '
                                f'{self.used_prefixes[ns.prefix]} and {str(ns.uri)}')
            return
        self.used_prefixes[ns.prefix] = str(ns.uri)
        self.fp.write(ns.format('turtle') + '\n')

    def flush(self):
        while self.buffer:
            self._write_one_from_buffer()

    def __del__(self):
        if self.buffer:
            raise Exception('Not all triples were written to the file (consider calling flush())')
