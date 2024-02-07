import json
import re
from io import StringIO

from lxml import etree

decl_regex = re.compile(r'(for all|for every|for any|where|let) (?P<formula>@MathNode:(\d+)@)')

with open('preprocessed-paper-A.json') as fp:
    document = json.load(fp)

doc_uri = document['document']   # document URI
# formulae are replaced by tokens, but the document contains the original formulae as annotations
token_to_html = {
    annotation['string']: annotation['annotation']['body']['html-value']
    for annotation in document['annotations'] if 'html-value' in annotation['annotation']['body']
}

records = []
for counter, match in enumerate(decl_regex.finditer(document['plaintext'])):
    # Target for the entire phrase
    target_uri = f'{doc_uri}#declphrase.{counter}.target'
    records.append({
        'type': 'FragmentTarget',
        'id': target_uri,
        'source': doc_uri,
        'selector': [
            {
                'type': 'OffsetSelector',
                'start': document['start-refs'][match.start()],
                'end': document['end-refs'][match.end()],
            }
        ]
    })
    # Annotation for the entire phrase
    records.append({
        'type': 'Annotation',
        'id': f'{doc_uri}#declphrase.{counter}.anno',
        'target': target_uri,
        'body': {
            'type': 'SimpleTagBody',
            'value': 'http://example.org/DeclarationPhrase',
        }
    })

    # we assume that the first <mi> element in the formula is the declared identifier
    nodes = etree.parse(StringIO(token_to_html[match.group('formula')])).xpath('//mi')
    if not nodes:   # no <mi> element found
        continue

    # target for the identifier
    target_uri = f'{doc_uri}#declvar.{counter}.target'
    records.append({
        'type': 'FragmentTarget',
        'id': target_uri,
        'source': doc_uri,
        'selector': [
            {
                'type': 'PathSelector',
                'startPath': f'node(//mi[@id="{nodes[0].get("id")}"])',
                'endPath': f'after-node(//mi[@id="{nodes[0].get("id")}"])',
            }
        ]
    })

    # annotation for the identifier
    records.append({
        'type': 'Annotation',
        'id': f'{doc_uri}#declvar.{counter}.anno',
        'target': target_uri,
        'body': {
            'type': 'SimpleTagBody',
            'value': 'http://example.org/DeclaredVariable',
        }
    })

with open('paper-A-annotations.json', 'w') as fp:
    json.dump(records, fp, indent=4)
