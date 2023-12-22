from collections import OrderedDict
from typing import Optional, Iterable

from spotterbase.corpora.interface import Corpus, Document, DocumentNotInCorpusException
from spotterbase.rdf import as_uri
from spotterbase.rdf.uri import Uri, UriLike
from spotterbase.utils import config_loader


class _Resolver:
    def __init__(self):
        self._corpora: OrderedDict[Uri, Corpus] = OrderedDict()

    def register_corpus(self, corpus: Corpus):
        self._corpora[corpus.get_uri()] = corpus

    def get_corpus(self, uri: UriLike) -> Optional[Corpus]:
        if uri in self._corpora:
            return self._corpora[as_uri(uri)]
        return None

    def get_document(self, uri: UriLike) -> Optional[Document]:
        document: Optional[Document] = None
        correct_corpus: Optional[Corpus] = None
        for corpus in self._corpora.values():
            try:
                correct_corpus = corpus
                document = corpus.get_document(as_uri(uri))
                break
            except DocumentNotInCorpusException:
                pass
        if correct_corpus is not None:
            # optimization: next time start with this corpus
            self._corpora.move_to_end(correct_corpus.get_uri(), last=False)
        return document

    def get_known_corpora(self) -> Iterable[Corpus]:
        yield from self._corpora.values()


Resolver: _Resolver = _Resolver()

if __name__ == '__main__':
    config_loader.auto()
    print('Known corpora:')
    for corpus in Resolver.get_known_corpora():
        print('   ', corpus.get_uri())
