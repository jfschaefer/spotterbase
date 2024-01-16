from collections import OrderedDict
from typing import Optional, Iterable

from spotterbase.corpora.interface import Corpus, Document, DocumentNotInCorpusException
from spotterbase.rdf import as_uri
from spotterbase.rdf.uri import Uri, UriLike
from spotterbase.utils import config_loader


class Resolver:
    _corpora: OrderedDict[Uri, Corpus] = OrderedDict()

    @classmethod
    def register_corpus(cls, corpus: Corpus):
        cls._corpora[corpus.get_uri()] = corpus

    @classmethod
    def get_corpus(cls, uri: UriLike) -> Optional[Corpus]:
        if uri in cls._corpora:
            return cls._corpora[as_uri(uri)]
        return None

    @classmethod
    def get_document(cls, uri: UriLike) -> Optional[Document]:
        document: Optional[Document] = None
        correct_corpus: Optional[Corpus] = None
        for corpus in cls._corpora.values():
            try:
                correct_corpus = corpus
                document = corpus.get_document(as_uri(uri))
                break
            except DocumentNotInCorpusException:
                pass
        if correct_corpus is not None:
            # optimization: next time start with this corpus
            cls._corpora.move_to_end(correct_corpus.get_uri(), last=False)
        return document

    @classmethod
    def get_known_corpora(cls) -> Iterable[Corpus]:
        yield from cls._corpora.values()


if __name__ == '__main__':
    config_loader.auto()
    print('Known corpora:')
    for corpus in Resolver.get_known_corpora():
        print('   ', corpus.get_uri())
