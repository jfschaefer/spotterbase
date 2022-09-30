from spotterbase.rdf.base import Uri
from spotterbase.sparql.endpoint import get_endpoint
from spotterbase.sparql.query import PREFIXES, json_binding_to_object, NAMESPACES
from spotterbase.spotters.simple_unit_spotter.all_units import get_all_units

def main():
    query = PREFIXES + '''
    SELECT ?s (count(?x) as ?relevance) WHERE {
        { ?s a om:PrefixedUnit } UNION { ?s a om:SingularUnit } .
        { ?s ?p ?x } UNION { ?x ?p ?s } .
    } GROUP BY ?s
    '''

    print(query)

    endpoint = get_endpoint()
    result = endpoint.get(query)
    # print(result)

    for var in result['head']['vars']:
        print(var.ljust(30), end=' ')
    print()
    for binding in result['results']['bindings']:
        for var in result['head']['vars']:
            value = json_binding_to_object(binding[var])
            as_string = str(value)
            if isinstance(value, Uri):
                value = value.with_namespace_from(NAMESPACES) or value
                as_string = format(value, ':')

            print(as_string.ljust(30), end=' ')
        print()


    all_units = get_all_units()
    print(all_units)
    print(len(all_units))
    symbols = {}
    for u in all_units:
        if u.symbol in symbols:
            print('Clash:', repr(u), repr(symbols[u.symbol]))
        symbols[u.symbol] = u

if __name__ == '__main__':
    main()
