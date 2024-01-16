.. _RDF intro:

A Brief Introduction to RDF
---------------------------

SpotterBase annotations are based on the `Resource Description Framework (RDF) <https://www.w3.org/RDF/>`_.
To an extent, you can use SpotterBase without understanding RDF,
but eventually it will be helpful to have at least a basic understanding of it.

This is not the place for a full introduction to RDF,
but we will try to give a brief overview of the relevant concepts.
This should enable you to read up on different aspects as needed.
Alternatively, you can also take a look at the `W3C RDF 1.1 Primer <https://www.w3.org/TR/rdf11-primer/>`_.

Representing data as triples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

RDF can be used to represent data as a set of triples
of the form ``subject predicate object``.
For example, we could represent the fact that
the document ``doc01`` has the topic ``topic01`` as the triple
``doc01 hasTopic topic01``.

In RDF, the subject, predicate and object are usually URIs, but literals and
anonymous nodes (called "blank nodes") are also possible.
Using URIs, we could represent the above fact as the triple

.. code-block:: turtle

    <http://example.org/doc01> <http://example.org/hasTopic> <http://example.org/topic01> .

We can use more triples to represent further facts:

.. code-block:: turtle

    <http://example.org/doc01> <http://example.org/hasAuthor> <http://example.org/authorX> .
    # for the name, we use a String literal
    <http://example.org/authorX> <http://example.org/hasName> "John Doe" .
    # similarly, we can use a number literal for the birth year
    <http://example.org/authorX> <http://example.org/birthYear> 1987 .

In general, we can use any URIs we want.
However, there are some well known vocabularies that define URIs for
various use cases.
For example, the `FOAF vocabulary <http://xmlns.com/foaf/spec/>`_
defines URIs for people, their names, etc.
So instead of using our made-up ``<http://example.org/hasName>`` predicate,
we could use the FOAF predicate ``<http://xmlns.com/foaf/0.1/name>``.


Prefixes
^^^^^^^^

In the above example, we used the full URIs for the predicates.
This can get tedious, and many RDF formats allow us to specify prefixes
for URIs.
For example, we could define the prefix ``foaf:`` for the FOAF vocabulary,
and then use ``foaf:name`` instead of the full URI
(``foaf:`` abbreviates ``<http://xmlns.com/foaf/0.1/>``).
This is particularly helpful as RDF vocabularies are usually based
on a namespace URI, and the actual URIs are defined by appending a name.
For example, we could now use ``foaf:workInfoHomepage`` to specify
the work website of a person.


Graphs
^^^^^^

We can also think of a set of triples as a graph,
where the subjects and objects are nodes and the predicates are edges.
The above example would look like this:

.. rdf:turtle:: rdf-example-graph
    :show: +graph -turtle

    @prefix ex: <http://example.org/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    ex:doc01 ex:hasTopic ex:topic01 .
    ex:doc01 ex:hasAuthor ex:authorX .
    ex:authorX foaf:name "John Doe" .
    ex:authorX ex:birthYear 1987 .


RDF formats
^^^^^^^^^^^

There are various formats for representing RDF data.
The most established one is `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_,
but it is not the most human-readable one.
`N-Triples <https://www.w3.org/TR/n-triples/>`_
is a very simple format where you simply write out the triples.
`Turtle <https://www.w3.org/TR/turtle/>`_ is a superset of N-Triples
that allows you to use prefixes and some other shortcuts.


Databases and queries
^^^^^^^^^^^^^^^^^^^^^

RDF triples can be stored in specialized databases, often called "triple stores".
They can then be queried using the `SPARQL query language <https://www.w3.org/TR/sparql11-query/>`_.
For example, we could query for all documents by "John Doe" with the following SPARQL query:

.. code-block:: sparql

    PREFIX ex: <http://example.org/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT ?doc WHERE {
        ?doc ex:hasAuthor ?author .
        ?author foaf:name "John Doe" .
    }
