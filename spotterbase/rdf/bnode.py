from __future__ import annotations


class BlankNode:
    _counter: int = 0

    def __init__(self):
        # must have unique value
        self.value = hex(BlankNode._counter)[2:]
        BlankNode._counter += 1

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def __str__(self):
        return f'_:{self.value}'

    @classmethod
    def reset_counter(cls):
        cls._counter = 0
