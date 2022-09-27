"""
A very hacky script to generate classes for commonly used vocabularies.
"""

import sys

import rdflib
import requests

VOCABULARIES = [
    ('AS', 'https://raw.githubusercontent.com/w3c/activitystreams/master/vocabulary/activitystreams2.owl',
     'http://www.w3.org/ns/activitystreams#'),
    ('DC', 'https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_elements.ttl',
     'http://purl.org/dc/elements/1.1/'),
    ('DCAM', 'https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_abstract_model.ttl',
     'http://purl.org/dc/dcam/'),
    ('DCTERMS', 'http://dublincore.org/2020/01/20/dublin_core_terms.ttl', 'http://purl.org/dc/terms/'),
    ('DCTYPES', 'https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_type.ttl',
     'http://purl.org/dc/dcmitype/'),
    ('FOAF', 'http://xmlns.com/foaf/0.1/index.rdf', 'http://xmlns.com/foaf/0.1/'),
    ('RDF', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    ('RDFS', 'http://www.w3.org/2000/01/rdf-schema#', 'http://www.w3.org/2000/01/rdf-schema#'),
    ('OA', 'http://www.w3.org/ns/oa.ttl', 'http://www.w3.org/ns/oa#'),
    ('OWL', 'http://www.w3.org/2002/07/owl#', 'http://www.w3.org/2002/07/owl#'),
    ('SKOS', 'https://www.w3.org/2009/08/skos-reference/skos.rdf', 'http://www.w3.org/2004/02/skos/core#')
    # XSD is hard-coded
]

PREFIXES = '''
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
'''


def create_from(ontology: str, namespace: str):
    graph = rdflib.Graph()
    response = requests.get(ontology)
    assert response.status_code == 200, f'Bad response code ({response.status_code}): {response.text}'
    # graph.parse(ontology, format='xml' if ontology.endswith('.rdf') else 'ttl')
    graph.parse(data=response.text, format='xml' if response.text.startswith('<') else 'ttl')

    # PROPERTIES
    property_results = graph.query(PREFIXES + '''
    SELECT ?prop ?comm WHERE {
        { ?prop a rdf:Property }
        UNION { ?prop a owl:ObjectProperty }
        UNION { ?prop rdfs:range ?range }
        UNION { ?prop rdfs:domain ?domain }
        OPTIONAL { ?prop rdfs:comment ?comm }
    }
    ''')
    comments = {row.prop: row.comm.strip().replace('\n', '\n    # ') for row in property_results if row.comm}
    properties = set(row.prop for row in property_results)
    if properties:
        print('    # PROPERTIES')
    for prop in sorted(properties):
        # assert prop.startswith(namespace), f'{prop} does not start with {namespace}'
        if not prop.startswith(namespace):
            continue
        if prop in comments:
            print('    # ' + comments[prop])
        print('    ' + prop[len(namespace):] + ': Uri')

    # CLASSES
    class_results = graph.query(PREFIXES + '''
    SELECT DISTINCT ?thing ?comm WHERE {
        { ?thing a rdfs:Class }
        UNION
        { ?thing a owl:Class }
        OPTIONAL { ?thing rdfs:comment ?comm }
    }
    ''')
    comments = {row.thing: row.comm.strip().replace('\n', '\n    # ') for row in class_results if row.comm}
    classes = set(row.thing for row in class_results)
    if classes:
        print('\n    # CLASSES')
    for class_ in sorted(classes):
        if class_ not in properties:
            # assert class_.startswith(namespace), f'{class_} does not start with {namespace}'
            if not class_.startswith(namespace):
                continue
            if class_ in comments:
                print('    # ' + comments[class_])
            print('    ' + class_[len(namespace):] + ': Uri')

    # OTHER
    other_results = graph.query(PREFIXES + f'''
    SELECT DISTINCT ?thing ?type ?comm WHERE {{
        ?thing a ?type
        FILTER (strstarts(str(?thing), '{namespace}'))
        OPTIONAL {{ ?thing rdfs:comment ?comm }}
    }}
    ''')
    comments = {row.thing: '\n    # '.join(line.strip() for line in row.comm.strip().splitlines()) for row in
                other_results if row.comm}
    covered = classes | properties
    printed_other = False
    for result in sorted(other_results, key=lambda r: r.thing):
        if '-' in result.thing[len(namespace):]:  # can't just use it as Python attribute
            continue
        if result.thing in covered:
            continue
        if len(result.thing) == len(namespace):
            continue
        if not printed_other:
            print('\n    # OTHER')
            printed_other = True
        if result.thing in comments:
            print('    # ' + comments[result.thing])
        covered.add(result.thing)
        name = result.thing[len(namespace):]
        print('    ' + name + ': Uri ' + max(0, 30 - len(name)) * ' ' + '# a ' + str(result.type))


def main():
    print('""" Commonly used RDF vocabularies (automatically generated) """\n')
    print('from spotterbase.rdf.base import Vocabulary, NameSpace, Uri\n')
    for classname, ontology, namespace in VOCABULARIES:
        print(f'Processing {ontology}', file=sys.stderr)
        print(f'\nclass {classname}(Vocabulary):')
        print(f'    """ Generated from {ontology} """\n')
        print(f"    NS = NameSpace(Uri('{namespace}'), prefix='{classname.lower()}:')\n")
        create_from(ontology, namespace)
        print()
    print('\nclass XSD(Vocabulary):')
    print("    NS = NameSpace(Uri('http://www.w3.org/2001/XMLSchema#'), prefix='xsd:')\n")
    for e in ['anyURI', 'base64Binary', 'boolean', 'byte', 'date', 'dateTime', 'dateTimeStamp', 'dayTimeDuration',
              'decimal', 'double', 'float', 'gDay', 'gMonth', 'gMonthDay', 'gYear', 'gYearMonth', 'hexBinary', 'int',
              'integer', 'language', 'long', 'Name', 'NCName', 'NMTOKEN', 'negativeInteger', 'nonNegativeInteger',
              'nonPositiveInteger', 'normalizedString', 'positiveInteger', 'short', 'string', 'time', 'token',
              'unsignedByte', 'unsignedInt', 'unsignedLong', 'unsignedShort', 'yearMonthDuration', 'precisionDecimal']:
        print(f'    {e}: Uri')


if __name__ == '__main__':
    main()
