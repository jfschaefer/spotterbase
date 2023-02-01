import datetime

from spotterbase.rdf.base import Literal
from spotterbase.rdf.vocab import XSD, RDF


class StringLiteral(Literal):
    def __init__(self, string: str):
        Literal.__init__(self, string=string, datatype=XSD.string)

    def __str__(self):
        # string literals do not require a datatype annotation
        return repr(self.string)   # does this always work?


class NonNegativeIntLiteral(Literal):
    def __init__(self, value: int):
        Literal.__init__(self, string=str(value), datatype=XSD.nonNegativeInteger)


class DateTimeLiteral(Literal):
    def __init__(self, dt: datetime.datetime):
        self.dt = dt
        Literal.__init__(self, string=dt.isoformat(), datatype=XSD.dateTime)


class FloatLiteral(Literal):
    def __init__(self, value: float):
        Literal.__init__(self, string=f'{value:e}', datatype=XSD.double)
        self.value = value


class LangString(Literal):
    def __init__(self, string: str, lang: str):
        Literal.__init__(self, string, datatype=RDF.langString, lang_tag=lang)
