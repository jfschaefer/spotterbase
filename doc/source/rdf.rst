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


Basics
------

URIs, namespaces
^^^^^^^^^^^^^^^^

Creating simple URIs
""""""""""""""""""""

URIs can be created with the :class:`~spotterbase.rdf.uri.Uri` class:

>>> from spotterbase.rdf import Uri, NameSpace, Vocabulary
>>> example = Uri('http://example.org')
>>> example
Uri('http://example.org')
>>> example / 'helloWorld'
Uri('http://example.org/helloWorld')
>>> (example / 'helloWorld').to_rdflib()
rdflib.term.URIRef('http://example.org/helloWorld')

Name spaces and vocabularies
""""""""""""""""""""""""""""

>>> from spotterbase.rdf import NameSpace, Vocabulary
>>> ns = NameSpace('http://example.org/', prefix='ex:')
>>> ns['helloWorld']
Uri('http://example.org/helloWorld')

Sometimes it is convenient to define the vocabulary concisely in one place.

>>> class Example(Vocabulary):
...     NS = NameSpace('http://example.org/', prefix='ex:')
...     helloWorld: Uri
>>> Example.helloWorld
Uri('http://example.org/helloWorld')

Some commonly use vocabularies are already in the library:

>>> from spotterbase.rdf import vocab
>>> vocab.RDF.type
Uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')

Formatting URIs and name spaces
"""""""""""""""""""""""""""""""

>>> ns = NameSpace('http://example.org/', prefix='ex:')
>>> uri = ns['hello/world']

Namespaces can be formatted for prefix declarations:

>>> format(ns, 'sparql')
'PREFIX ex: <http://example.org/>'
>>> format(ns, 'turtle')   # short: format(ns, 'ttl')
'@prefix ex: <http://example.org/> .'

URIs can be formatted in the following ways:

>>> format(uri)   # same as str(uri) and format(uri, 'plain')
'http://example.org/hello/world'
>>> format(uri, '<>')
'<http://example.org/hello/world>'
>>> format(uri, 'prefix')   # short: format(uri, ':')
'ex:hello\\/world'
>>> # if no prefix is provided:
>>> format(Uri('http://example.org/hello/world'), 'prefix')
'<http://example.org/hello/world>'

Some software does not support prefixed URIs if reserved characters are escaped (e.g. Virtuoso).
``'nrprefix`` only uses a prefix if there are no reserved characters are in the suffix:
>>> format(uri, 'nrprefix')
'<http://example.org/hello/world>'
>>> format(ns['hello'], 'nrprefix')
'ex:hello'


Literals
^^^^^^^^

Creating literals
"""""""""""""""""

>>> from spotterbase.rdf import Literal
>>> Literal('hello world')
"hello world"
>>> Literal('123', vocab.XSD.integer)
"123"^^<http://www.w3.org/2001/XMLSchema#integer>
>>> Literal('hello', lang_tag='en')
"hello"@en

We can also create them from Python values:

>>> Literal.from_py_val(42)
"42"^^<http://www.w3.org/2001/XMLSchema#integer>
>>> Literal.from_py_val(42, datatype=vocab.XSD.nonNegativeInteger)
"42"^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>


Using literals
""""""""""""""

We turn (some) literals into Python values:

>>> Literal('2023-03-29T16:43:42.509531', vocab.XSD.dateTime).to_py_val()
datetime.datetime(2023, 3, 29, 16, 43, 42, 509531)


Formatting literals
"""""""""""""""""""

>>> l = Literal.from_py_val(3.2)
>>> format(l, 'ttl')
'3.200000E+00'
>>> format(l, 'nt')
'"3.200000E+00"^^<http://www.w3.org/2001/XMLSchema#double>'


Blank nodes
^^^^^^^^^^^

Whenever you instantiate a new :class:`spotterbase.rdf.bnode.BlankNode`, it gets a new value using a counter.
We use a counter to have relatively short names for blank nodes to keep the generated RDF files small.
The disadvantage is that (unlike when using e.g. UUIDs) we have to be much more careful if blank nodes
are created from multiple processes.

>>> from spotterbase.rdf import BlankNode
>>> BlankNode.reset_counter()   # for reproducability
>>> a = BlankNode()
>>> a
BlankNode(0)
>>> str(a)
'_:0'
>>> b = BlankNode()
>>> str(b)
'_:1'


Triples
^^^^^^^

Triples are represented as Python tuples:

>>> ns = NameSpace('http://example.org/', prefix='ex:')
>>> triple = (ns['s'], ns['p'], ns['o'])


Serialization
-------------

Let's make some triples:

>>> food = NameSpace('http://example.org/food/', prefix='food:')
>>> triples = [
...     (food['apple'], vocab.RDF.type, food['fruit']),
...     (food['apple'], vocab.RDFS.label, Literal.lang_tagged('Apfel', 'de'))]

Normally, the serializer should write to a file,
but for this small example we will use :class:`io.StringIO` for better illustration:

>>> from spotterbase.rdf import TurtleSerializer
>>> import io
>>> file = io.StringIO()
>>> with TurtleSerializer(file) as serializer:
...     serializer.write_comment('example')
...     serializer.add_from_iterable(triples)
>>> print(file.getvalue().strip())
# example
@prefix food: <http://example.org/food/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
food:apple a food:fruit ;
  rdfs:label "Apfel"@de .

The :class:`spotterbase.rdf.serializer.NTriplesSerializer` works analogously.
The :class:`spotterbase.rdf.serializer.FileSerializer` gets a path as an argument
and writes to that file instead, inferring the correct serialization format from the file name.


Conversion to ``rdflib``
------------------------

Triples can be converted to ``rdflib`` with the :mod:`spotterbase.rdf.to_rdflib` module.
Note that the conversion requires a state to keep track of blank nodes.

