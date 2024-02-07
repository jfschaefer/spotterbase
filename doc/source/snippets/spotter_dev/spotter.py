import re
from datetime import datetime

from spotterbase.dnm.defaults import ARXMLIV_STANDARD_DNM_FACTORY
from spotterbase.model_core import SpotterRun, Annotation, SimpleTagBody
from spotterbase.rdf import TripleI, Uri
from spotterbase.rdf.namespace_collection import EXAMPLE
from spotterbase.selectors.dom_range import DomRange
from spotterbase.spotters.spotter import Spotter, SpotterContext


class ExampleDeclSpotter(Spotter):
    spotter_short_id = 'example-decl-spotter'

    @classmethod
    def setup_run(cls, **kwargs) -> tuple[SpotterContext, TripleI]:
        run = SpotterRun(
            uri=Uri.uuid(),
            spotter_uri=EXAMPLE['exampledeclarationspotter'],
            spotter_version='0.0.1',
            date=datetime.now(),
            label='Simple Part-Of-Speech Tagger based on NLTK'
        )
        return SpotterContext(run_uri=run.uri), run.to_triples()

    def process_document(self, document) -> TripleI:
        dnm = ARXMLIV_STANDARD_DNM_FACTORY.dnm_from_document(document)
        decl_regex = re.compile(r'(for all|for every|for any|where|let) (?P<formula>@MathNode:(\d+)@)')
        for counter, match in enumerate(decl_regex.finditer(str(dnm))):
            math_node = dnm[match.start('formula'):match.end('formula')].to_dom().get_containing_node()
            identifier = math_node.xpath('//mi')
            if not identifier:
                continue

            target_uri = f'{document.get_uri()}#declvar.{counter}.target'
            yield from document.get_selector_converter().dom_to_fragment_target(
                target_uri, DomRange.from_node(identifier[0])
            ).to_triples()
            yield from Annotation(
                f'{document.get_uri()}#declvar.{counter}.anno',
                target_uri=target_uri,
                body=SimpleTagBody(EXAMPLE['DeclarationVariable']),
                creator_uri=self.ctx.run_uri,
            ).to_triples()


if __name__ == '__main__':
    from spotterbase.spotters import spotter_runner
    spotter_runner.auto_run_spotter(ExampleDeclSpotter)
