:mod:`~spotterbase.rdf` package
===============================

The :mod:`~spotterbase.rdf` package provides basic functionality for working with RDF triples.
In particular, it supports:

* Managing namespaces, URIs and literals
* Serializing triples


What about ``rdflib``?
----------------------

There is already a big Python library for working with RDF: `rdflib <https://rdflib.readthedocs.io/en/stable/index.html>`_.
The :mod:`~spotterbase.rdf` package supports mapping to and from ``rdflib``.

So why do we reinvent the wheel?
The original reason was the wish to serialize large numbers of triples without accumulating them in a graph first (which sometimes requires too much memory).
Nevertheless, it might be a good idea to replace more of the :mod:`~spotterbase.rdf` package with ``rdflib``.


Overview
--------

The basics: URIs, literals, namespaces
**************************************

Let's create some URIs:

>>> from spotterbase.rdf import Uri, NameSpace, Vocabulary
>>> example = Uri('http://example.org')
>>> example
Uri('http://example.org')
>>> example / 'helloWorld'
Uri('http://example.org/helloWorld')
>>> (example / 'helloWorld').to_rdflib()
rdflib.term.URIRef('http://example.org/helloWorld')

And the same with Namespaces:

>>> ns = NameSpace('http://example.org/', prefix='ex:')
>>> ns['helloWorld']
Uri('http://example.org/helloWorld')
>>> # IDEs support class attributes better than strings - the following is also possible:
>>> class Example(Vocabulary):
...     NS = NameSpace('http://example.org/', prefix='ex:')
...     helloWorld: Uri
>>> Example.helloWorld
Uri('http://example.org/helloWorld')

Some commonly use vocabularies are already in the library:

>>> from spotterbase.rdf import vocab
>>> vocab.RDF.type
Uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')

Here is a literal:

>>> from spotterbase.rdf import Literal
>>> Literal.from_py_val(5.3, vocab.XSD.double)
"5.300000E+00"^^<http://www.w3.org/2001/XMLSchema#double>

If a :class:`~spotterbase.rdf.base.NameSpace` has a prefix,
we can format it and its derived URIs nicely:

>>> format(ns, 'turtle')
'@prefix ex: <http://example.org/> .'
>>> format(ns, 'sparql')
'PREFIX ex: <http://example.org/>'
>>> format(ns['helloWorld'], 'prefix')
'ex:helloWorld'
>>> # Without the association, it cannot work:
>>> format(Uri('http://example.org/helloWorld'), 'prefix')
'<http://example.org/helloWorld>'


Triples and serialization
*************************

Let's make some triples:

>>> food = NameSpace('http://example.org/food/', prefix='food:')
>>> triples = [
...     (food['apple'], vocab.RDF.type, food['fruit']),
...     (food['apple'], vocab.RDFS.label, Literal.lang_tagged('Apfel', 'de'))]
>>> from spotterbase.rdf import TurtleSerializer

Normally, the serializer should write to a file,
but for this small example we will use :class:`io.StringIO` for better illustration:

>>> import io
>>> file = io.StringIO()
>>> with TurtleSerializer(file) as serializer:
...     serializer.add_from_iterable(triples)
>>> print(file.getvalue().strip())
@prefix food: <http://example.org/food/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
food:apple a food:fruit ;
  rdfs:label "Apfel"@de .

