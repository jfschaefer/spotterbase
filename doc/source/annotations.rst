:mod:`~spotterbase.annotations` package
=======================================

The :mod:`~spotterbase.annotations` package provides classes for representing
annotations and converting them to different formats.


Selectors
---------

``sb:SbPathSelector``
---------------------

``sb:SbOffsetSelector``
-----------------------


JSON format for annotations
---------------------------

For many applications, RDF triples are not the most convenient format for representing annotations.
As an alternative, SpotterBase can import and export annotations in a JSON format.
Concretely, the JSON format is based on `JSON-LD <https://json-ld.org/>`_,
which has been developed as a format for sharing linked data.
In principle, the JSON data can therefore be directly loaded into a triple store.

We have decided to fix a subset of JSON-LD for annotations, which can be supported
by different applications more directly (i.e. without translating it into triples).
The hope is that makes the development of applications much easier, especially for people
not familiar with RDF and SPARQL.

.. literalinclude:: codesnippets/example-annotation.jsonld
    :language: JSON-LD


Design decisions
----------------

Cardinality of targets and bodies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

According to the web annotation specification, an annotation can have multiple targets or bodies.
If it has multiple targets/bodies, the each body refers to each target individually.
If an annotation is supposed to target multiple things together, a single composite target should be used instead.

We decided not to support multiple targets/bodies in SpotterBase to simplify things.
The reasoning is multiple targets/bodies for a single annotation would make it much more difficult
to have "meta annotations", e.g. indicating if an annotation is correct (what if it is correct for one target, but not the other?).

Furthermore, annotations without a body are also not supported by SpotterBase (to keep things simple).

Discontinuous targets are supported via selector refinements.


Custom selectors
^^^^^^^^^^^^^^^^

Instead of making custom selectors, we could have used existing selectors (with a custom format for the ``oa:FragmentSelector``).
We decided against it as it results in substantially more triples.
Consider, for example, these triples with our custom selector:


.. code-block:: Turtle

    _:selector rdf:type sb:PathSelector .
    _:selector sb:startPath  "node(/html/body/p[2]/math[3])" .
    _:selector sb:endPath  "node(/html/body/p[2]/math[5])" .


might have these triples if expressed with the standard selectors:

.. code-block:: Turtle

    _:selector rdf:type oa:RangeSelector .
    _:selector oa:hasStartSelector _:start_selector .
    _:selector oa:hasEndSelector _:end_selector .

    _:start_selector rdf:type oa:FragmentSelector .
    _:start_selector rdf:value "node(/html/body/p[2]/math[3])" .
    _:start_selector dc:conformsTo sb:pathFragmentSelector .

    _:end_selector rdf:type oa:FragmentSelector .
    _:end_selector rdf:value "node(/html/body/p[2]/math[5])" .
    _:end_selector dc:conformsTo sb:pathFragmentSelector .

The translation to/from standard selectors is easy enough that we could support them as well if necessary.

