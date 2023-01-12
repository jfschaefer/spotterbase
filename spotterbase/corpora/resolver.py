from collections import OrderedDict
from typing import Optional

from spotterbase.corpora.interface import Corpus, Document, DocumentNotInCorpusException
from spotterbase.rdf.base import Uri


class _Resolver:
    def __init__(self):
        self._corpora: OrderedDict[Uri, Corpus] = OrderedDict()

    def register_corpus(self, corpus: Corpus):
        self._corpora[corpus.get_uri()] = corpus

    def get_corpus(self, uri: Uri) -> Optional[Corpus]:
        if uri in self._corpora:
            return self._corpora[uri]
        return None

    def get_document(self, uri: Uri) -> Optional[Document]:
        document: Optional[Document] = None
        correct_corpus: Optional[Corpus] = None
        for corpus in self._corpora.values():
            try:
                correct_corpus = corpus
                document = corpus.get_document(uri)
                break
            except DocumentNotInCorpusException:
                pass
        if correct_corpus is not None:
            # optimization: next time start with this corpus
            self._corpora.move_to_end(correct_corpus.get_uri(), last=False)
        return document


Resolver: _Resolver = _Resolver()
