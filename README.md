# Spotterbase


## Installation
```
git clone https://github.com/jfschaefer/spotterbase
cd spotterbase
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

You can run the unittests to see if everything has worked:
```
python3 -m spotterbase.test
```


## Spotters and importers
While this repository contains some spotters and importers, most of them are located at [https://github.com/jfschaefer/spotters](https://github.com/jfschaefer/spotters).


## Example commands
Tip: Every command has a `--help` option.

Note that documents and corpora are identified by their URI.
If you want to use a different corpus, e.g. [arXMLiv](https://sigmathling.kwarc.info/resources/arxmliv-dataset-2020/),
you can download it and specify its location via the options, e.g.
```
python -m spotterbase.preprocessing.html_tokenize --document=http://sigmathling.kwarc.info/arxmliv/2020/0704.1635 --output='out.html' --arxmliv-2020-path=/drive/arxivnlp/dataset-arxmliv-2020
```


### Running the POS Tag spotter
This requires installing `nltk` (`python3 -m pip install nltk`) and its part-of-speech data (`python3 -c 'import nltk; nltk.download("universal_tagset")'`).
```
python3 -m spotterbase.spotters.example_spotters.simple_pos_tag_spotter --document=http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA --dir=pos_tag_results
```


### Document pre-processing
```
python3 -m spotterbase.preprocessing.html_tokenize --document=http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA --output='tokenized.html'
python3 -m spotterbase.preprocessing.document_to_json --document=http://sigmathling.kwarc.info/spotterbase/test-corpus/paperA --output='tokenized.json'
```


### Annotations to JSON-LD
Requires an (uncompressed) file of RDF annotations. For example, after running the POS tagger, we can extract the results with
```
gunzip pos_tag_results/spostag.nt.gz
```
and then run
```
python3 -m spotterbase.records.rdf_to_jsonld --file=pos_tag_results/spostag.nt --output=spostag.jsonld
```

Note: By default, rdflib is used. This gets very slow for larger graphs.
You can specify a different endpoint, e.g.
```
python3 -m spotterbase.records.rdf_to_jsonld --file=pos_tag_results/spostag.nt --output=spostag.jsonld --work-sparql-endpoint 'Virtuoso()'
```
if you have Virtuoso installed and running locally.


### Other commands
Use `--help` to learn about the command line arguments
* `spotterbase.corpora.arxiv_metadata_rdf_gen` to generate arxiv metadata annotations.
* `spotterbase.corpora.arxmliv_metadata_rdf_gen` to generate metadata annotations for an arXMLiv corpus (links to arXiv metadata).
* `spotterbase.corpora.write_document_to_file` to write document to a file (useful, e.g., if the corpus is a compressed arxiv).
* `spotterbase.corpora.resolver` lists locally available corpora.
* `spotterbase.spotters.example_spotters.simple_declaration_spotter` a spotter for declarations.
* `spotterbase.spotters.example_spotters.simple_substring_spotter` spotters that check if the HTML sources contain a substring (useful to pre-select interesting documents).



## Documentation
Currently, the documentation is not hosted anyway.
You can generate it with
```bash
cd doc
make html
```
This will probably require you to install a few more packages with pip.
and then open `doc/build/html/index.html` in your browser.
