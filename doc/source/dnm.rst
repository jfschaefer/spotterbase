:mod:`~spotterbase.rdf` package
===============================

A DNM (Document Narrative Model) is an plaintext representation that is linked to the DOM (Document Object Model).


DNM factories
-------------

DNMs are created from a DOM in a DNM factory.
The factory allows for custom DNM generation, e.g. it might be desirable to skip or replace certain nodes.


>>> from spotterbase.corpora.test_corpus import TEST_DOC_A
>>> from spotterbase.dnm.simple_dnm_factory import SimpleDnmFactory
>>> factory = SimpleDnmFactory()
>>> dnm = factory.dnm_from_document(TEST_DOC_A)
>>> dnm[:80]
Dnm('\n\nTest Document: There are interesting triangles\n\n\n\n\n\n\n\nTest Document: There are')


We can customize the factory by, e.g., replacing some nodes:


>>> factory = SimpleDnmFactory(nodes_to_replace={'title': '', 'math': 'MathNode'})
>>> dnm = factory.dnm_from_document(TEST_DOC_A)
>>> dnm[:80]
Dnm('\n\n\n\n\n\n\n\n\n\nTest Document: There are interesting triangles\n\n\nNota Mathematician\n\n\n')


In general, the ``ARXMLIV_STANDARD_DNM_FACTORY`` is a good starting point.


DNMs as strings
---------------

