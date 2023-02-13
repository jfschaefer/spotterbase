import abc
from collections import OrderedDict, defaultdict
from typing import TextIO, Iterable, Optional

from spotterbase.rdf.base import Triple, Uri, Object, NameSpace, Subject, BlankNode, Predicate, Literal
from spotterbase.rdf.vocab import RDF


class Serializer(abc.ABC):
    def add(self, s: Subject, p: Predicate, o: Object):
        raise NotImplementedError()

    def add_from_iterable(self, triples: Iterable[Triple]):
        for triple in triples:
            self.add(*triple)

    def flush(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()


class TurtleSerializer(Serializer):
    # https://www.w3.org/TR/turtle/#sec-grammar-grammar
    def __init__(self, fp: TextIO, buffer_size: int = 100000):
        self.fp = fp
        self.max_buffer_size = buffer_size
        self.cur_buffer_size = 0
        self.buffer: OrderedDict[Subject, list[tuple[Predicate, Object]]] = OrderedDict()
        self.used_prefixes: dict[str, str] = {}

    def add(self, s: Subject, p: Predicate, o: Object):
        if s in self.buffer:
            self.buffer[s].append((p, o))
            self.buffer.move_to_end(s)
        else:
            self.buffer[s] = [(p, o)]
        self.cur_buffer_size += 1
        if self.cur_buffer_size >= self.max_buffer_size:
            self._write_one_from_buffer()

    def _write_one_from_buffer(self):
        subject, pairs = self.buffer.popitem(last=False)
        self.cur_buffer_size -= len(pairs)

        # make sure all prefixes have been created
        if isinstance(subject, Uri):
            self._require_prefix(subject.namespace)
        prop_to_obj = defaultdict(list)
        for prop, obj in pairs:
            assert isinstance(prop, Uri), f'{prop!r} was used as a predicate but is not a Uri'
            self._require_prefix(prop.namespace)
            if isinstance(obj, Uri):
                self._require_prefix(obj.namespace)
            prop_to_obj[prop].append(obj)

        # write triples
        self._write_node(subject)
        first_prop = True
        for prop, objs in prop_to_obj.items():
            if first_prop:
                self.fp.write(' ')
                first_prop = False
            else:
                self.fp.write(' ;\n  ')
            if prop == RDF.type:
                self.fp.write('a')
            else:
                self._write_node(prop)
            first_obj = True
            for obj in objs:
                if first_obj:
                    self.fp.write(' ')
                    first_obj = False
                else:
                    self.fp.write(',\n    ')
                self._write_node(obj)
        self.fp.write(' .\n')

    def _write_node(self, node: Subject | Predicate | Object):
        match node:
            case Uri():
                # use 'nrprefix' because virtuoso seems to have problems with prefix:path\/to\/something
                self.fp.write(format(node, 'nrprefix'))
            case BlankNode():
                self.fp.write(f'_:{node.value}')
            case Literal():
                self.fp.write(str(node))
            case _:
                raise NotImplementedError(f'Unsupported node type {type(node)}')

    def _require_prefix(self, ns: Optional[NameSpace]):
        if not ns or not ns.prefix:
            return
        if ns.prefix in self.used_prefixes:
            if self.used_prefixes[ns.prefix] != str(ns.uri):
                raise Exception(f'Prefix "{ns.prefix}" used for two different namespaces: '
                                f'{self.used_prefixes[ns.prefix]} and {str(ns.uri)}')
            return
        self.used_prefixes[ns.prefix] = str(ns.uri)
        self.fp.write(f'{ns:turtle}\n')

    def flush(self):
        while self.buffer:
            self._write_one_from_buffer()

    def __del__(self):
        if self.buffer:
            raise Exception('Not all triples were written to the file (consider calling flush())')


class NTriplesSerializer(Serializer):
    def __init__(self, fp: TextIO):
        self.fp = fp

    def add(self, s: Subject, p: Predicate, o: Object):
        self._write_node(s)
        self.fp.write(' ')
        self._write_node(p)
        self.fp.write(' ')
        self._write_node(o)
        self.fp.write(' .\n')

    def _write_node(self, node: Subject | Predicate | Object):
        # TODO: almost same as in TurtleSerializer
        match node:
            case Uri():
                self.fp.write(format(node, '<>'))
            case BlankNode():
                self.fp.write(f'_:{node.value}')
            case Literal():
                self.fp.write(str(node))
            case _:
                raise NotImplementedError(f'Unsupported node type {type(node)}')
