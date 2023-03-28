from typing import TextIO, Iterator

from spotterbase.rdf import Triple


def deserialize_nt(fp: TextIO, skip_comments: bool = False) -> Iterator[Triple | str]:
    """ Only supports a subset of NT """
    for line in fp:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            yield line[1:].strip()
        else:
            ...
