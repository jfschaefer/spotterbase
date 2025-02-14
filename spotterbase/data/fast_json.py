""" Faster JSON loading.

The json module in the standard library is somewhat slow.
This module provides JSON functionality from faster libraries,
but falls back to the standard library if the faster libraries are not installed.

At the moment, the only supported faster library is orjson,
but this might change in the future.
"""
import io
import json
import logging
import typing

from spotterbase.utils.logging import warn_once

try:
    import orjson
except ModuleNotFoundError:
    orjson = None  # type: ignore

logger = logging.getLogger(__name__)


def orjson_check() -> bool:
    if orjson is None:
        warn_once(logger, 'orjson is not installed, using json instead (this might be slower)')
        return False
    return True


def load(fp: typing.IO):
    if orjson_check():
        return orjson.loads(fp.read())   # loads supports bytes and str
    return json.load(fp)        # works for binary files and text files


def loads(s: str):
    if orjson_check():
        return orjson.loads(s)
    return json.loads(s)


def dump_bytes(obj, fp: typing.BinaryIO):   # potentially faster than dump_text if orjson is available
    if orjson_check():
        fp.write(orjson.dumps(obj))
    else:
        fp.write(json.dumps(obj).encode())


def dump_text(obj, fp: typing.TextIO):
    if orjson_check():
        fp.write(orjson.dumps(obj).decode())
    else:
        json.dump(obj, fp)


def dump(obj, fp: typing.TextIO):
    if isinstance(fp, io.TextIOBase):
        return dump_text(obj, fp)   # type: ignore
    else:
        assert isinstance(fp, io.BufferedIOBase) or isinstance(fp, io.RawIOBase)
        return dump_bytes(obj, fp)   # type: ignore
