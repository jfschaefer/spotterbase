from __future__ import annotations

from typing import Iterable, TypeAlias

from spotterbase.rdf.bnode import BlankNode
from spotterbase.rdf.literal import Literal
from spotterbase.rdf.uri import Uri

Subject: TypeAlias = Uri | BlankNode
Predicate: TypeAlias = Uri
Object: TypeAlias = Uri | BlankNode | Literal
Triple: TypeAlias = tuple[Subject, Predicate, Object]
TripleI: TypeAlias = Iterable[Triple]
