import re

from spotterbase.corpora.resolver import Resolver
from spotterbase.dnm.defaults import ARXMLIV_STANDARD_DNM_FACTORY
from spotterbase.model_core import SimpleTagBody, Annotation
from spotterbase.rdf import FileSerializer
from spotterbase.rdf.namespace_collection import EXAMPLE
from spotterbase.selectors.dom_range import DomRange

decl_regex = re.compile(r'(for all|for every|for any|where|let) (?P<formula>@MathNode:(\d+)@)')

document = Resolver.get_document('https://ns.mathhub.info/project/sb/data/test-corpus/paperA')
dnm = ARXMLIV_STANDARD_DNM_FACTORY.dnm_from_document(document)

records = []
for counter, match in enumerate(decl_regex.finditer(str(dnm))):
    # annotate phrase
    target_uri = f'{document.get_uri()}#declphrase.{counter}.target'
    records.append(dnm[match].to_fragment_target(target_uri))
    records.append(
        Annotation(
            f'{document.get_uri()}#declphrase.{counter}.anno',
            target_uri=target_uri,
            body=SimpleTagBody(EXAMPLE['DeclarationPhrase']),
        )
    )

    math_node = dnm[match.start('formula'):match.end('formula')].to_dom().get_containing_node()
    identifier = math_node.xpath('//mi')
    if not identifier:
        continue

    # annotate identifier
    target_uri = f'{document.get_uri()}#declvar.{counter}.target'
    records.append(document.get_selector_converter().dom_to_fragment_target(
        target_uri, DomRange.from_node(identifier[0])
    ))
    records.append(
        Annotation(
            f'{document.get_uri()}#declvar.{counter}.anno',
            target_uri=target_uri,
            body=SimpleTagBody(EXAMPLE['DeclarationVariable']),
        )
    )

# write records to RDF file
with FileSerializer('paper-a-decl.ttl') as serializer:
    for record in records:
        serializer.add_from_iterable(record.to_triples())
