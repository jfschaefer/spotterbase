:mod:`~spotterbase.convert` package
===================================

The :mod:`~spotterbase.convert` can be used to
convert a document into an easier-to-process format
with information for linking annotations back to the original document.
Currently, the following formats are supported:

* a JSON-based format where each word is represented as a JSON object,
* an HTML-based format where each word is wrapped in a ``<span>``.

The conversion code can be used from the command line or from Python code.

:mod:`~spotterbase.convert` also can be used to recover and normalize
annotation targets.

Preprocessing to JSON
---------------------

The convert to JSON results in an easy-to-use JSON document.
Every word is represented as a JSON object with the its offsets.
Example word:

.. code-block:: json

    {
     "token": "triangle",
     "start-ref": 302,
     "end-ref": 310
    }


Example call:

.. code-block:: bash

    python3 -m spotterbase.convert.document_to_json \
       --include-replaced-nodes \
       --document=http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA \
       --output=tokenized.json

With the ``--include-replaced-nodes`` option, the will contain the
HTML nodes for tokens that were created by replacing a node
(e.g. a ``<math>`` node for ``"MathNode"`` tokens).


If you want to use the preprocessor from Python code, you have to use the
:class:`~spotterbase.convert.document_to_json.Doc2JsonConverter`, e.g.:

>>> from spotterbase.convert.document_to_json import Doc2JsonConverter
>>> from spotterbase.corpora.resolver import Resolver
>>> document = Resolver.get_document('http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA')
>>> converter = Doc2JsonConverter(include_replaced_nodes=True, skip_titles=True)
>>> json_document = converter.process(document)


Preprocessing to HTML
---------------------

