import abc
import gzip
import pickle
from collections import OrderedDict, defaultdict
from io import StringIO
from pathlib import Path
from typing import TextIO, Iterable, Optional, BinaryIO

from spotterbase.rdf.literal import Literal
from spotterbase.rdf.types import Subject, Predicate, Object, Triple, TripleI
from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.uri import NameSpace, Uri
from spotterbase.rdf.vocab import RDF


class Serializer(abc.ABC):
    def add(self, s: Subject, p: Predicate, o: Object):
        raise NotImplementedError()

    def add_from_iterable(self, triples: Iterable[Triple]):
        for triple in triples:
            self.add(*triple)

    def write_comment(self, s: str):
        raise NotImplementedError()

    def flush(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.flush()


class FileSerializer(Serializer):
    def __init__(self, path: Path | str, append: bool = False):
        self.path = Path(path)
        self.serializer: Serializer
        name = self.path.name

        if name.endswith('.gz'):
            self.fp = gzip.open(path, 'at' if append else 'wt')
            name = name[:-3]
        else:
            self.fp = open(path, 'a' if append else 'w')

        if name.endswith('.ttl'):
            self.serializer = TurtleSerializer(self.fp)
        elif name.endswith('.nt'):
            self.serializer = NTriplesSerializer(self.fp)
        else:
            self.fp.close()
            raise Exception('Unsupported file extension')

    def close(self):
        self.serializer.close()
        self.fp.close()

    def add(self, s: Subject, p: Predicate, o: Object):
        self.serializer.add(s, p, o)

    def add_from_iterable(self, triples: Iterable[Triple]):
        self.serializer.add_from_iterable(triples)

    def write_comment(self, s: str):
        self.serializer.write_comment(s)

    def flush(self):
        self.serializer.flush()


class TurtleSerializer(Serializer):
    # https://www.w3.org/TR/turtle/#sec-grammar-grammar
    def __init__(self, fp: TextIO, buffer_size: int = 1024, fixed_prefixes: Optional[Iterable[NameSpace]] = None,
                 write_prefixes: bool = True):
        self.fp = fp
        self.max_buffer_size = buffer_size
        self.cur_buffer_size = 0
        self.buffer: OrderedDict[Subject, list[tuple[Predicate, Object]]] = OrderedDict()
        self.used_prefixes: dict[str, str] = {}
        self.write_prefixes = write_prefixes
        self.allow_new_prefixes = True
        if fixed_prefixes:
            for ns in fixed_prefixes:
                self._require_prefix(ns)
        self.allow_new_prefixes = fixed_prefixes is None

    def write_comment(self, s: str):
        self.flush()
        self.fp.write('# ' + s.replace('\n', '\n# ') + '\n')

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
        if isinstance(node, Uri):
            # use 'nrprefix' because virtuoso seems to have problems with prefix:path\/to\/something
            if node.namespace and node.namespace.prefix in self.used_prefixes:
                self.fp.write(format(node, 'nrprefix'))
            else:
                self.fp.write(format(node, '<>'))
        elif isinstance(node, BlankNode):
            self.fp.write(f'_:{node.value}')
        elif isinstance(node, Literal):
            self.fp.write(node.to_turtle())
        else:
            raise NotImplementedError(f'Unsupported node type {type(node)}')

    def _require_prefix(self, ns: Optional[NameSpace]):
        if not self.allow_new_prefixes or not ns or not ns.prefix:
            return
        if ns.prefix in self.used_prefixes:
            if self.used_prefixes[ns.prefix] != str(ns.uri):
                raise Exception(f'Prefix "{ns.prefix}" used for two different namespaces: '
                                f'{self.used_prefixes[ns.prefix]} and {str(ns.uri)}')
            return
        self.used_prefixes[ns.prefix] = str(ns.uri)
        if self.write_prefixes:
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

    def write_comment(self, s: str):
        self.fp.write('# ' + s.replace('\n', '\n# ') + '\n')

    def add(self, s: Subject, p: Predicate, o: Object):
        self._write_node(s)
        self.fp.write(' ')
        self._write_node(p)
        self.fp.write(' ')
        self._write_node(o)
        self.fp.write(' .\n')

    def _write_node(self, node: Subject | Predicate | Object):
        if isinstance(node, Uri):
            self.fp.write(format(node, '<>'))
        elif isinstance(node, BlankNode):
            self.fp.write(f'_:{node.value}')
        elif isinstance(node, Literal):
            self.fp.write(node.to_ntriples())
        else:
            raise NotImplementedError(f'Unsupported node type {type(node)}')


def triples_to_nt_string(triples: TripleI) -> str:
    strio = StringIO()
    with NTriplesSerializer(strio) as serializer:
        serializer.add_from_iterable(triples)
    return strio.getvalue()


def triples_to_turtle(triples: TripleI) -> str:
    strio = StringIO()
    with TurtleSerializer(strio) as serializer:
        serializer.add_from_iterable(triples)
    return strio.getvalue()


class PickleSerializer(Serializer):
    def __init__(self, fp: BinaryIO):
        self.fp = fp

    def add(self, s: Subject, p: Predicate, o: Object):
        pickle.dump((s, p, o), self.fp)


def triples_from_pickle(file: BinaryIO | Path) -> TripleI:
    def load_from_fp(fp: BinaryIO):
        try:
            while True:
                yield pickle.load(fp)
        except EOFError:
            pass

    if isinstance(file, Path):
        with open(file, 'rb') as fp:
            yield from load_from_fp(fp)
            return
    return load_from_fp(file)
