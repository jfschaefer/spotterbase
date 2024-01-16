Developing a spotter
====================

In this tutorial, we will discuss four different approaches to developing a spotter,
which increasingly leverage the SpotterBase codebase.

Along the way, we will develop multiple spotters that build on each other's results.


Formula Spotter (spotter that does not use SpotterBase)
-------------------------------------------------------

You do not have to use SpotterBase at all and can simply
implement code that creates annotations in the right format
(either in the JSON format or as RDF triples).
Often, the SpotterBase command line tools might be helpful anyway,
but for some applications, their usefulness might be very limited.

As an example, we will create a spotter that annotates for documents whether
they contain a formula or not.

Here is a simple implementation of such a spotter:

.. literalinclude:: snippets/spotter_dev/formula_spotter.py
    :language: python


In this example, we use Python, but you can use any programming language.
The example creates a Turtle file (``mathcheck.ttl``) that contains the annotations.
Another option would have been to create a JSON file.


We can now upload the annotations into a triple store and query them.
For example, we might want to find all documents that contain a formula
so that we can process them with the next spotters (processing documents
without formulae would be a waste of resources).
Here is a SPARQL query that does this:

.. literalinclude:: snippets/spotter_dev/doc_query.sparql
    :language: sparql


Approach 2: Only use SpotterBase command line tools
---------------------------------------------------

You can use the SpotterBase command line tools (documented `here <_cmdtoools>`_)
for pre-processing documents.

As an example, we will create a spotter that looks for the phrases like
"let ..." or "for all ...", and annotates the formula that follows.
In the next approach, we will use these annotations to build a spotter that
extracts the identifiers that were introduced.

Step 1: Pre-process the document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Working with HTML documents is difficult (especially as we also want to get
the annotation targets right). Therefore, we will convert the HTML document
to a JSON file using the `JSON pre-processing tool <_cmdtools-preprocess-json>`_ that comes with SpotterBase.
There are different variants of the pre-processing tool (see the documentation for more details).

Let us pre-process a document from the example corpus:

.. literalinclude:: snippets/spotter_dev/preprocess.sh
    :language: bash


Step 2: Write the actual spotter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the pre-processed document, math nodes are replaced with a token.
We will look for patterns like `"for all @MathNode:3@"`.
The document also contains the MathML of the node, which we can
use to extract the identifier.




