import re

from lxml import etree

from spotterbase import config_loader
from spotterbase.data.arxiv import ArxivId
from spotterbase.data.arxmliv import ArXMLiv
from spotterbase.dnm.dnm import DnmStr
from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators


def main():
    config_loader.auto()

    arxmliv = ArXMLiv()
    corpus = arxmliv.get_corpus('2020')
    document = corpus.get_document(ArxivId('hep-ph/9803374'))
    tree = etree.parse(document.open(), parser=etree.HTMLParser())

    dnm = TokenBasedDnm.from_token_generator(tree, DefaultGenerators.ARXMLIV_TEXT_ONLY)

    dnmstr = dnm.get_dnm_str()
    # print(dnmstr)

    for match in re.finditer('MathNode', dnmstr.string):
        substr: DnmStr = dnmstr[match]
        point = substr.as_range().to_dom().as_point()
        if not point or not point.is_element():
            print('OOPS')
            continue

        node = point.node


if __name__ == '__main__':
    main()