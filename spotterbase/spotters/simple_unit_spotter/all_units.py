import dataclasses

from spotterbase.rdf.base import Uri
from spotterbase.sparql.endpoint import get_endpoint
from spotterbase.sparql.query import PREFIXES


@dataclasses.dataclass
class Unit:
    """ A unit, possible with a prefix """
    uri: Uri
    symbol: str         # notation
    relevance: int


def get_all_units() -> list[Unit]:
    query = PREFIXES + '''
    SELECT ?unit ?symbol (count(?x) as ?relevance) WHERE {
        { ?unit a om:SingularUnit } UNION { ?unit a om:PrefixedUnit } .
        { ?unit om:symbol ?symbol } .
        { ?unit ?p ?x } UNION { ?x ?p ?unit } .
    } GROUP BY ?unit ?symbol ORDER BY DESC(?relevance)
    '''
    endpoint = get_endpoint()
    results = []
    for r in endpoint.query(query):
        results.append(Unit(r['unit'], r['symbol'].string, int(r['relevance'].string)))
    return results


def without_duplicate_symbols(units: list[Unit]) -> list[Unit]:
    results = []
    used_symbols: set[str] = set()
    for unit in sorted(units, key=lambda u: u.relevance, reverse=True):   # should be sorted from sparql query, but let's make sure
        if unit.symbol not in used_symbols:
            used_symbols.add(unit.symbol)
            results.append(unit)
    return results
