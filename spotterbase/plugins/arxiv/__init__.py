from spotterbase.plugins.arxiv.ar5iv import AR5IV_CORPUS
from spotterbase.plugins.arxiv.arxmliv import ARXMLIV_CORPORA


def load():
    from spotterbase.corpora.resolver import Resolver
    for corpus in ARXMLIV_CORPORA.values():
        Resolver.register_corpus(corpus)
    Resolver.register_corpus(AR5IV_CORPUS)
