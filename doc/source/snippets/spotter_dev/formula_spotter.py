# We use SpotterBase only to get the directory of the test corpus
from spotterbase.corpora.test_corpus import TEST_CORPUS_DIR

with open("mathcheck.ttl", "w") as fp:
    fp.write("@prefix oa: <http://www.w3.org/ns/oa#> .\n")
    fp.write("@prefix sb: <https://ns.mathhub.info/project/sb/> .\n")
    fp.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
    fp.write("@prefix dcterms: <http://purl.org/dc/terms/> .\n\n")

    for path in sorted(TEST_CORPUS_DIR.glob('*.html')):
        doc_uri = "https://ns.mathhub.info/project/sb/data/test-corpus/" + path.name[:-5]
        if "</math>" in path.read_text():       # very crude check
            tag = "http://example.org/mathspotter-result#contains-math"
        else:
            tag = "http://example.org/mathspotter-result#no-math"

        anno_uri = doc_uri + "#mathcheckanno"   # can be anything, but must be unique
        fp.write(f"\n<{anno_uri}> a oa:Annotation ;\n")
        fp.write(f"    oa:hasTarget <{doc_uri}> ;\n")
        fp.write(f"    oa:hasBody [\n")
        fp.write(f"        a sb:SimpleTagBody ;\n")
        fp.write(f"        rdf:value <{tag}> ;\n")
        fp.write(f"    ] ;\n")
        fp.write(f"    dcterms:creator <http://example.org/mathspotter> .\n")
