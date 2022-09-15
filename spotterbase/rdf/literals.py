import datetime

from spotterbase.rdf.base import Literal
from spotterbase.rdf.vocab import XSD


class StringLiteral(Literal):
    def __init__(self, string: str):
        Literal.__init__(self, string=string, datatype=XSD.string)

    def __str__(self):
        return repr(self.string)   # does this always work?


class DateTimeLiteral(Literal):
    def __init__(self, dt: datetime.datetime):
        self.dt = dt
        Literal.__init__(self, string=dt.isoformat(), datatype=XSD.dateTime)


