
```shell
# Install
sudo apt install  virtuoso-opensource

# Optional: Custom config
cp /usr/share/virtuoso-opensource-6.1/virtuoso.ini .
vim virtuoso.ini

# In folder with `virtuoso.ini`
virtuoso-t -fd
```

Conductor interface: http://localhost:8890/conductor/
(by default on port 8890)

Default admin credentials: `dba`, `dba`.

Follow this website https://vos.openlinksw.com/owiki/wiki/VOS/VirtRDFInsert#HTTP%20POST%20Example%201

the following should work
```shell
curl --verbose --digest --user "spotterbase:spotterbasepwd" -T centi-arxiv-metadata.ttl.gz --url 'http://localhost:8890/sparql-graph-crud-auth?graph-uri=http%3A//sigmathling.kwarc.info/test2' -H 'Content-Type: text/turtle' -H 'Content-Encoding: gzip'
```
but doesn't because of https://github.com/openlink/virtuoso-opensource/issues/764

Possible solution: gunzip in /tmp first (works without gzip)
