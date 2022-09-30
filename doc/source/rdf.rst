:mod:`~spotterbase.rdf` package
===============================

The :mod:`~spotterbase.rdf` package provides basic functionality for working with RDF triples.


What about ``rdflib``?
----------------------

There is already a big Python library for working with RDF: `rdflib <https://rdflib.readthedocs.io/en/stable/index.html>`_.
The :mod:`~spotterbase.rdf` package supports mapping to and from ``rdflib``.

So why do we reinvent the wheel?
The original reason was the wish to serialize large numbers of triples without accumulating them in a graph first (which sometimes requires too much memory).
Nevertheless, it might be a good idea to replace more of the :mod:`~spotterbase.rdf` package with ``rdflib``.





