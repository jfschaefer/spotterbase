Developing a spotter
====================

In this tutorial, we will discuss four different approaches to developing a spotter,
which increasingly leverage the SpotterBase codebase.

Along the way, we will develop multiple spotters that build on each other's results.


Formula Spotter (does not use SpotterBase)
------------------------------------------

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


Declaration spotter (only uses SpotterBase command line tools)
--------------------------------------------------------------

You can use the SpotterBase command line tools (documented `here <_cmdtoools>`_)
for pre-processing documents.

As an example, we will create a spotter that looks for the phrases like
"let ..." or "for all ..." and annotates the phrase and the declared identifier in the formula.
E.g. for "let x ∈ ℝ", we would annotate "let x ∈ ℝ" as a declaration phrase and "x" as the declared identifier.
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
The spotter (for didactic reasons) creates two annotations for each declaration:
one for the entire phrase and one for the declared identifier.
Here is a simple implementation of such a spotter:

.. literalinclude:: snippets/spotter_dev/ext_decl_spotter.py
    :language: python

In this case, the spotter creates a JSON file,
following the SpotterBase JSON format
(the `annotation format page <_Annotation Format>`_ has more details).


Step 3: Selector normalization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The annotations created by the spotter are not exactly in the right format.
Some only use the ``OffsetSelector``, others only use the ``PathSelector``
(and does not use the simple absolute XPaths recommended).
SpotterBase provides a tool that normalizes the selectors:

.. literalinclude:: snippets/spotter_dev/normalize_selectors.sh
    :language: bash

.. TODO: We can also convert to e.g. Turtle with SB.



Another declaration spotter (uses SpotterBase as a library)
-----------------------------------------------------------

In this approach, we will create the same declaration spotter as in the previous approach,
but we will use SpotterBase as a library.
Instead of running the pre-processing to obtain a plaintext document,
we can use the `DNM library <_DNM>`_ to obtain a plaintext representation.

Here is an implementation of the spotter:

.. literalinclude:: snippets/spotter_dev/sblib_decl_spotter.py
    :language: python

In this case, the script generates RDF triples in the Turtle format,
instead of a JSON file as in the previous approach.
We could have generated a JSON file as well, but we can also
convert the Turtle file to JSON using the SpotterBase command line tools:

.. literalinclude:: snippets/spotter_dev/anno_rdf_to_jsonld.sh
    :language: bash



Yet another declaration spotter (uses SpotterBase as a framework)
-----------------------------------------------------------------

When running a spotter over a large corpus, we typically need some more infrastructure work.
Spotters should run in parallel, we want to have an idea of the progress,
we might want to interrupt the processing and resume it later,
we might want to run multiple spotters without re-parsing the HTML documents for each spotter, etc.
SpotterBase provides a framework that takes care of these issues.

Here is a simple example how that works (we only annotation the declared identifiers in this case):

.. literalinclude:: snippets/spotter_dev/spotter.py
    :language: python

We can run the spotter over the example document with the following command:

.. literalinclude:: snippets/spotter_dev/run_spotter.sh
    :language: bash

