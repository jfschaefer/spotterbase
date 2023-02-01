import gzip
import re
from typing import Optional

from lxml import etree

import spotterbase.utils.xml_match as xm
from spotterbase import config_loader, __version__
from spotterbase.corpora.arxiv import ArxivId
from spotterbase.corpora.arxmliv import ArXMLiv
from spotterbase.dnm.selectors import SbRangeSelector
from spotterbase.sb_vocab import SB
from spotterbase.dnm.dnm import DnmStr, DnmRange
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators
from spotterbase.rdf.base import BlankNode
from spotterbase.rdf.literals import FloatLiteral
from spotterbase.rdf.serializer import TurtleSerializer
from spotterbase.rdf.vocab import OA, RDF
from spotterbase.spotters.rdfhelpers import SpotterRun, Annotation
from spotterbase.spotters.simple_unit_spotter import patterns, all_units
from spotterbase.spotters.simple_unit_spotter.om_vocab import OM
from spotterbase.spotters.simple_unit_spotter.patterns import scalar_to_scalars


def main():
    om_units = {
        u.symbol: u for u in all_units.without_duplicate_symbols(all_units.get_all_units())
    }

    with gzip.open(f'/tmp/test.ttl.gz', 'wt') as fp:
        fp.write(f'# Graph: {SB.NS["graph/simple-unit-spotter"]:<>}\n')
        serializer = TurtleSerializer(fp)

        spotter_run = SpotterRun(SB.NS.uri / 'spotter' / 'simple-units', spotter_version=__version__)

        serializer.add_from_iterable(spotter_run.triples())


        config_loader.auto()

        arxmliv = ArXMLiv()
        corpus = arxmliv.get_corpus('2020')
        document = corpus.get_document(ArxivId('hep-ph/9803374'))   # https://ar5iv.labs.arxiv.org/html/hep-ph/9803374
        tree = etree.parse(document.open(), parser=etree.HTMLParser())

        dnm = TokenBasedDnm.from_token_generator(tree, DefaultGenerators.ARXMLIV_TEXT_ONLY)

        dnmstr = dnm.get_dnm_str()
        # print(dnmstr)

        for re_match in re.finditer('MathNode', dnmstr.string):
            substr: DnmStr = dnmstr[re_match]
            point = substr.as_range().to_dom().as_point()
            if not point or not point.is_element():
                print('OOPS')
                continue

            node = point.node
            root = xm.tag('math')**'root' / xm.tag('semantics')
            matcher = root / patterns.scalar   # patterns.quantity | patterns.quantity_in_rel
            matches = list(matcher.match(node))
            # print(matches)
            if not matches:
                continue
            if len(matches) > 1:
                # print('OOPS 2')
                continue
            match = matches[0]
            # print(match)
            # unit = unit_to_unit_notation(match['unit'])
            scalar = scalar_to_scalars(match['scalar'])
            remainder = dnmstr[re_match.end():]
            if len(remainder) > 5 and remainder[0] == ' ':
                unit: Optional[DnmStr] = None
                for i in range(1, 5):
                    if remainder[i] == ' ':
                        unit = remainder[1:i]
                if not unit:
                    continue
                print(list(SbRangeSelector(DnmRange(substr.as_range().from_, unit.as_range().to).to_dom()).to_triples()[1]))
                if str(unit) not in om_units:
                    print('do not know', unit)
                    continue

                selector, triples = DnmRange(substr.as_range().from_, unit.as_range().to).to_dom()
                annotation = Annotation(spotter_run)
                target = BlankNode()
                body = BlankNode()
                annotation.add_target(target)
                annotation.add_body(body)

                serializer.add_from_iterable(annotation.triples())
                serializer.add_from_iterable([
                    (target, OA.hasSelector, selector),
                    (target, OA.hasSource, document.get_uri()),
                ])
                serializer.add_from_iterable(triples)

                serializer.add_from_iterable([
                    (body, RDF.type, OM.Measure),
                    (body, OM.hasNumericalValue, FloatLiteral(scalar.value)),
                    (body, OM.hasUnit, om_units[str(unit)]._suffix),
                ])

        serializer.flush()


if __name__ == '__main__':
    main()
