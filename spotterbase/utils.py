from spotterbase.__version__ import VERSION


def version_string() -> str:
    return '.'.join(str(e) for e in VERSION)
