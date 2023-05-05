:mod:`~spotterbase.corpora` package
===================================

The :mod:`~spotterbase.corpora` package provides functionality for working
with corpora (in particular the arXMLiv corpus).


Using the :class:`~spotterbase.corpora.resolver.Resolver`
---------------------------------------------------------

The ``Resolver`` can be used to load a document if you have its URI.
Usually, it is required that you have downloaded the corpus and SpotterBase is able to find it.
SpotterBase comes with a test corpus, which we will use for the examples:

>>> from spotterbase.corpora.resolver import Resolver
>>> from spotterbase.rdf import Uri
>>> uri = Uri('http://sigmathling.kwarc.info/spotterbase/test-corpus/')
>>> corpus = Resolver.get_corpus(uri)
>>> for document in corpus:
...     print(document.get_uri())
http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA
http://sigmathling.kwarc.info/spotterbase/test-corpus/paperB
>>> document = corpus.get_document(uri / 'paperB')
>>> # alternatively, we can get the document directly from the Resolver:
>>> document = Resolver.get_document(uri / 'paperB')
>>> document.get_uri()
Uri('http://sigmathling.kwarc.info/spotterbase/test-corpus/paperB')
>>> with document.open() as fp:
...     print(fp.read(21))
<!DOCTYPE html><html>


Corpus metadata
---------------

:mod:`~spotterbase.corpora` also contains scripts to create the metadata associated with a corpus.
This should include linking all documents to their corpus.
It can also include annotations such as the classification of the document.


Adding another corpus
---------------------

The :mod:`spotterbase.corpora.test_corpus` module has an implementation of a simple corpus.
You should be able to adapt it to your own needs.
If you want it to be supported by the :class:``~spotterbase.corpora.resolver.Resolver``, you will have to register it.

