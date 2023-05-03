""" Provides blank nodes.

Notes from compression efficiency experiment (with turtle file, using a typical amount of blank nodes):
    * Using a counter -> 37 MB (gzipped; uncompressed: 790 MB)
    * Using uuid4 -> 75 MB (gzipped)
    * Using uuid1 -> 38 MB (gzipped; uncompressed: 886 MB)
    * using uuid1 with fake MAC | PID and increasing clock_seq -> 48 MB (gzipped)
    * using uuid1 with fake MAC | PID and no (i.e. random) clock_seq -> 50 MB (gzipped)

Another option (even more memory efficient than uuid1, also when not compressed):
    start = hex(int(10*time.time()))[2:]
    counter = 0
    def get_value():
        global counter
        return start + '-' + hex(os.getpid())[2:] + '-' + hex(counter)[2:] + '\n'
        counter += 1

TODO: The current design should be improved (e.g. by switching to factories and having a default factory in BlankNode,
      which is used in __new__)
"""

from __future__ import annotations

import contextlib
import itertools
import random
import uuid
from typing import Optional, ClassVar, TypeAlias, Iterator

BlankNodeFactory: TypeAlias = Iterator['BlankNode']


def anonymized_uuid1_factory() -> Iterator[BlankNode]:
    _uuid_mask: int = random.getrandbits(128)    # to mask the MAC address for privacy
    while True:
        guid = uuid.uuid1()
        # assert guid.is_safe == uuid.SafeUUID.safe
        yield BlankNode(hex(guid.int ^ _uuid_mask)[2:])


def counter_factory(start: int = 0) -> Iterator[BlankNode]:
    for i in itertools.count(start):
        yield BlankNode(hex(i)[2:])


def uuid4_factory() -> Iterator[BlankNode]:
    while True:
        yield BlankNode(uuid.uuid4().hex)


class BlankNode:
    __slots__ = ('value',)
    _factory: ClassVar[BlankNodeFactory] = anonymized_uuid1_factory()

    def __new__(cls, value: Optional[str] = None):
        if value is None:
            return next(cls._factory)
        return super().__new__(cls)

    def __init__(self, value: Optional[str] = None):
        if hasattr(self, 'value'):   # This happens if __new__ returns an object that was already initialized
            return
        assert value is not None, 'value is None but __new__ should have prevented that'
        self.value: str = value

    @classmethod
    def get_factory(cls) -> BlankNodeFactory:
        return cls._factory

    @classmethod
    def overwrite_factory(cls, factory: BlankNodeFactory):
        cls._factory = factory

    @classmethod
    @contextlib.contextmanager
    def use_factory(cls, factory: BlankNodeFactory):
        previous_factory = cls._factory
        try:
            cls.overwrite_factory(factory)
            yield
        finally:
            cls._factory = previous_factory

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def __str__(self):
        return f'_:{self.value}'

    def __eq__(self, other) -> bool:
        return isinstance(other, BlankNode) and self.value == other.value

    def __hash__(self):
        return hash(self.value)
