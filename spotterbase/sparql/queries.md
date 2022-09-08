# SPARQL Queries


Assuming the following prefixes:
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX oa: <http://www.w3.org/ns/oa#>

PREFIX sb: <http://sigmathling.kwarc.info/spotterbase/>
# arxiv categories
PREFIX axc: <https://arxiv.org/archive/>
```


#### All loaded spotter runs

```sparql
SELECT DISTINCT ?run ?spotter ?version ?date WHERE {
    ?run a sb:spotterRun .
    OPTIONAL { ?run sb:withSpotter ?spotter . }
    OPTIONAL { ?run sb:spotterVersion ?version . }
    OPTIONAL { ?run sb:runDate ?date . }
}
```

#### All arxiv documents of a particular category

```sparql
SELECT DISTINCT ?document WHERE {
    ?document a sb:document .
    ?anno oa:hasTarget ?document .
    ?anno oa:hasBody axc:q-bio.SC .
}
```
