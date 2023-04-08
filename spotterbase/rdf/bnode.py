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
import enum
import uuid
import random
from typing import Optional, ClassVar


class BNodeGenMode(enum.IntEnum):
    ANONYMIZED_UUID1 = enum.auto()
    UUID4 = enum.auto()
    COUNTER = enum.auto()


DEFAULT_MODE: BNodeGenMode = BNodeGenMode.ANONYMIZED_UUID1


class BlankNode:
    __slots__ = ('value',)
    _counter: ClassVar[int] = 0
    _uuid_mask: ClassVar[int] = random.getrandbits(128)
    _mode: BNodeGenMode = DEFAULT_MODE

    def __init__(self, value: Optional[str] = None):
        if value is None:
            mode = type(self)._mode
            if mode == BNodeGenMode.ANONYMIZED_UUID1:
                guid = uuid.uuid1()
                # assert guid.is_safe == uuid.SafeUUID.safe
                value = hex(guid.int ^ type(self)._uuid_mask)[2:]
            elif mode == BNodeGenMode.UUID4:
                value = uuid.uuid4().hex
            elif mode == BNodeGenMode.COUNTER:
                value = hex(type(self)._counter)[2:]
                type(self)._counter += 1
            else:
                raise Exception(f'Unsupported mode {mode}')

        self.value = value

    @classmethod
    def get_mode(cls) -> BNodeGenMode:
        return cls._mode

    @classmethod
    def reset_mode(cls):
        cls._mode = DEFAULT_MODE

    @classmethod
    @contextlib.contextmanager
    def set_counter_mode(cls, start: Optional[int] = None):
        if start is not None:
            cls._counter = start
        return cls.set_mode(BNodeGenMode.COUNTER)

    @classmethod
    def set_counter_mode_simple(cls, start: Optional[int] = None):
        if start is not None:
            cls._counter = start
        cls._mode = BNodeGenMode.COUNTER

    @classmethod
    @contextlib.contextmanager
    def set_mode(cls, mode: BNodeGenMode):
        previous_mode = cls._mode
        cls._mode = mode
        try:
            yield
        finally:
            cls._mode = previous_mode

    @classmethod
    def set_mode_simple(cls, mode: BNodeGenMode):
        cls._mode = mode

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def __str__(self):
        return f'_:{self.value}'

    def __eq__(self, other) -> bool:
        return isinstance(other, BlankNode) and self.value == other.value

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def reset_counter(cls):
        cls._counter = 0
