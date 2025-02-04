The :mod:`~spotterbase.plugins.arxiv` plugin
============================================

The arxiv plugin provides support for arXiv/arXMLiv/ar5iv documents.


Metadata generation
-------------------

arxiv metadata
^^^^^^^^^^^^^^

Creates a large RDF file with metadata about arxiv documents.
At the moment, this mostly links documents to corpora and arxiv categories.
More metadata can be added in the future (e.g. publications dates).

The data is extracted from `arXiv Dataset on kaggle <https://www.kaggle.com/Cornell-University/arxiv>`_.

.. code-block:: bash

    python3 -m spotterbase.plugins.arxiv.arxiv_metadata_rdf_gen \
        --arxiv-raw-metadata=path/to/arxiv-metadata-oai-snapshot.json.zip


arXMLiv metadata
^^^^^^^^^^^^^^^^

Requires the arXMLiv dataset to be downloaded.

.. code-block:: bash

    python3 -m spotterbase.plugins.arxiv.arxmliv_metadata_rdf_gen \
        --arxmliv-release=2020 \
        --arxmliv-2020-path=path/to/arxmliv-2020


