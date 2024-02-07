.. _Annotation Format:

SpotterBase Annotation Format
=============================


In SpotterBase, annotations are represented as sets of RDF triples.
In particular, the representation is based on the recommendations of the
`W3C Web Annotation Working Group <https://www.w3.org/annotation/>`_.

Annotations can be represented in different ways, and SpotterBase
can convert between them.
SpotterBase often uses chunks of information, which we call **records** (e.g. an annotation).
A record can be represented in different formats:

* A JSON format based on `JSON-LD <https://www.w3.org/TR/json-ld/>`_.
  This hides the RDF nature of the annotations, but with
  the right JSON-LD context it can be directly imported into a triple store.
  Each JSON object corresponds to a record.
* A set of RDF triples.
* A Python object.


.. todo:: Reference record documentation.

SpotterBase can convert between these formats.

To an extent, you can use SpotterBase without knowing RDF (e.g. if you
only use the JSON format),
but it is nevertheless useful to understand the underlying RDF model.
:ref:`RDF intro` might be a good place to start learning about RDF.

Annotations
-----------

.. rdf:record:: example-annotation

    {
        "type": "Annotation",
        "id": "http://sigmathling.kwarc.info/arxmliv/2020/math/0511246#meta.severity.anno",
        "target": "http://sigmathling.kwarc.info/arxmliv/2020/math/0511246",
        "body": {
            "type": "SimpleTagBody",
            "val": "http://sigmathling.kwarc.info/arxmliv/severity/error"
        },
        "creator": "http://sigmathling.kwarc.info/spotterbase/spotter/arxmlivmetadata"
    }


Following the recommendations of the `W3C Web Annotation Working Group <https://www.w3.org/annotation/>`_,
an annotation has two main components: a **target** and a **body**.
The target indicates what gets annotated, and the body contains information that should be associated with the target.
The annotation above, for example, indicates that the document
``http://sigmathling.kwarc.info/arxmliv/2020/math/0511246`` (the *target*)
was created by arXMLiv with the severity ``error`` (the *body*).
In this case, the body is a simple tag, but we can also have more complex bodies.

Every annotation must have a unique identifier (the ``"id"`` field in the JSON format).
This could be anything, but it can be helpful to use an identifier based on the document that is being annotated.

Annotations can also have a **creator** (in this case the annotation was created by a script).
A separate record can provide more information about the creator.


Targets
-------

The example annotation in the `Annotations`_ section targets an entire document.
In practice, however, we usually want to annotate only a part (a fragment) of a document like a word or a formula.

We can do this by creating a ``FragmentTarget`` record, like the following one:

.. rdf:record:: example-target

    {
        "type": "FragmentTarget",
        "id": "http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA#spostag.target.41",
        "source": "http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA",
        "selector": [
            {
                "type": "PathSelector",
                "startPath": "char(/html/body/div/div/article/section/div[2]/div/p/span,82)",
                "endPath": "char(/html/body/div/div/article/section/div[2]/div/p/span,84)"
            },
            {
                "type": "OffsetSelector",
                "start": 411,
                "end": 413
            }
        ]
    }

A ``FragmentTarget`` record has the following fields:

* ``"id"``:
  A unique identifier for the target.
  This identifier can be used in annotations to refer to the target.
* ``"source"``:
  The document that contains the fragment.
* ``"selector"``:
  A list of selectors that specify the fragment.
  Each selector should specify the same fragment.
  The selectors suggested by the Web Annotation Working Group were insufficient (or at least inconvenient) for our purposes,
  so SpotterBase supports two custom selectors: ``PathSelector`` and ``OffsetSelector``.
  While both selectors specify the same fragment, they have different advantages and disadvantages depending on the application.

.. tip::

   SpotterBase can convert between the two selectors.
   If you write a spotter, you only need to create one of them and SpotterBase can create the other one for you.


The ``PathSelector``
^^^^^^^^^^^^^^^^^^^^

The ``PathSelector`` selects a document range
by specifying the start and the end of the fragement.
Following the Web Annotation Recommandations,
the end is exclusive, i.e. the specified end is not part of the fragment.

The specification is based on `XPath <https://www.w3.org/TR/xpath/>`_.
Concretely, three types of expression are supported:

* ``char(xpath, n)``:
  Selects the n-th character of text inside the tag specified by the XPath expression.
  The XPath should not select a text node, but a tag that contains text.
  Text in nested tags is also counted.
* ``node(xpath)``:
  Selects the node specified by the XPath expression.
* ``after-node(xpath)``:
  Selects the point right after the node specified by the XPath expression.
  This is useful for the end of the fragment (the end is excluded, so ``after-node`` lets you effectively include the node).

.. important::

   SpotterBase assumes that documents are *static*.
   It is designed to deal with "frozen" corpora, not with documents that change over time.
   That makes the XPath expressions much less brittle.
   Nevertheless, there are some things to keep in mind:

   * Some HTML parsers (including browsers) insert additional tags into the document.
     The main example we are aware of is the insertion of a ``<tbody>`` tag into tables.
   * ``char`` expressions should count characters.
     For example, in JavaScript, the ``length`` property of a string counts UTF-16 code units, not characters.


.. note::

   While in principle arbitrary XPath expressions are supported,
   simple absolute paths are preferred as they can be processed efficiently
   and are supported by a wide range of tools.


The ``OffsetSelector``
^^^^^^^^^^^^^^^^^^^^^^

The ``OffsetSelector`` can select document ranges with the same granularity as the ``PathSelector``,
but it uses offsets instead of XPath expressions.
The offsets essentially count every opening tag, closing tag and character in text nodes.
While this is more difficult to emulate in other tools,
it has two key advantages:

* Offsets can be represented much more compactly.
* Offsets can be compared easily, e.g. to check if one target is contained in another one.

Aside from SpotterBase-internal uses, you might encounter the ``OffsetSelector`` in two other places:

* When you write a spotter using pre-processed files, they typically only references based on the ``OffsetSelector``
  as they are much more compact.
  SpotterBase can then convert them to a ``PathSelector`` for you.
* In SPARQL queries, you can use the ``OffsetSelector``
  to compare targets (e.g. to check if a word annotation is contained in a paragraph annotation).


Discontinuous fragments
^^^^^^^^^^^^^^^^^^^^^^^

The ``PathSelector`` and ``OffsetSelector`` can only select continuous fragments.
To select discontinuous fragments, the selectors can be refined with a ``ListSelector``,
which lists selectors for the ranges that make up the discontinuous fragment.

The ``ListSelector`` should only be used as a refinement of a selector that
selects the complete range of the fragment.
That way, tools that do not support discontinuous fragments can still process the annotation.

The selectors in a ``ListSelector`` should have the same type as the selector that is refined.

Here is an example of a discontinuous fragment using the ``OffsetSelector``:


.. rdf:record:: listselector-example

    {
        "type": "OffsetSelector",
        "start": 752,
        "end": 773,
        "refinedBy": {
            "type": "ListSelector",
            "vals": [
                {
                    "type": "OffsetSelector",
                    "start": 752,
                    "end": 761
                },
                {
                    "type": "OffsetSelector",
                    "start": 767,
                    "end": 773
                }
            ]
        }
    }

.. note::

   In the RDF representation, the selectors in the ``ListSelector``
   are represented as a linked list (using ``rdf:first``, ``rdf:rest`` and ``rdf:nil``).
   This allows to represent a closed list despite the open world assumption of RDF.
   Despite the list-like nature of the representation, the order of the selectors is not significant.

   For SPARQL queries, you can use the ``rdf:rest*/rdf:first`` property path to get all selectors in the list.


Bodies
------

In principle, the body of an annotation can be any RDF resource.
This is key to the flexibility of the annotation model and was a primary reason for using RDF in the first place.

For consistency, however, SpotterBase supports a few standard types of bodies.

Annotating with tags
^^^^^^^^^^^^^^^^^^^^

Single tags
~~~~~~~~~~~

The ``SimpleTagBody`` is a simple body that only contains a tag.
For example, the following body can be used to tag a word as a noun:

.. rdf:record:: simpletagbody-example

    {
        "type": "SimpleTagBody",
        "val": "http://sigmathling.kwarc.info/spotterbase/universal-pos-tags#NOUN"
    }


Multiple tags
~~~~~~~~~~~~~

For multiple tags, the ``MultiTagBody`` can be used.
For example, the following body can be used to annotate the area(s) a paper is about:

.. rdf:record:: multitagbody-example

    {
        "type": "MultiTagBody",
        "val": [
            "https://arxiv.org/archive/math.DS",
            "https://arxiv.org/archive/math.NA",
            "https://arxiv.org/archive/math"
        ]
    }

.. note::

   The ``MultiTagBody`` does not use an RDF collection to represent the tags.
   This makes querying easier and reduces the number of triples per annotation significantly.
   However, it is also somewhat problematic due to the open world assumption of RDF
   (it could contain more tags than the ones we are aware of).
   In practice, this should not be too much of a problem, though.


Tags and tag sets
~~~~~~~~~~~~~~~~~

Tags can be arbitrary RDF resources.
More information about tags can be provided in ``Tag`` records.
For example, the following record provides information about the tag ``NOUN``:

.. rdf:record:: tag-example

    {
        "type": "Tag",
        "id": "http://sigmathling.kwarc.info/spotterbase/universal-pos-tags#NOUN",
        "belongsTo": "http://sigmathling.kwarc.info/spotterbase/universal-pos-tags",
        "label": "NOUN",
        "comment": "nouns (common and proper)"
    }

Tags can belong to a tag set. In this case, the ``NOUN`` tag belongs to a set of POS tags.
We can also provide more information about the tag set in a ``TagSet`` record:

.. rdf:record:: tagset-example


    {
        "type": "TagSet",
        "id": "http://sigmathling.kwarc.info/spotterbase/universal-pos-tags",
        "label": "Universal Part-Of-Speech Tagset",
        "comment": "See https://arxiv.org/abs/1104.2086 for more information"
    }


Creators
--------

Annotations should have a creator.
That is especially important if we want to compare annotations from different sources and have them in the same database.
For example, we might have two people annotating the same document and then want to compute the inter-annotator agreement.
Similarly, we might want to evaluate a spotter by comparing its annotations to a gold standard.

The creator of an annotation (``creator`` field) can be any RDF resource.
SpotterBase also offers records to provide more information about creators.

For example, the ``SpotterRun`` record can be used to provide information about a spotter run.
Each run of a spotter should have a unique identifier.
That makes it possible to compare annotations from different runs of the same spotter.

Here is an example of a ``SpotterRun`` record:

.. rdf:record:: spotterrun-example

    {
        "type": "SpotterRun",
        "id": "urn:uuid:96233573-e637-4c88-aa2b-24cfcd627496",
        "withSpotter": "http://sigmathling.kwarc.info/spotterbase/ext/spotters#spostag",
        "spotterVersion": "0.0.2",
        "label": "Simple Part-Of-Speech Tagger based on NLTK",
        "created": "2024-01-04T12:46:12.475054"
    }

