"""This script runs all the snippets to ensure they are up-to-date."""
import gzip
import json
import tempfile
from pathlib import Path

import rdflib
from rdflib import Graph

from spotterbase.utils.snippet_runner_utils import run_python_file, run_shell_file


def assert_nonempty_json_file(file: Path):
    assert file.is_file()
    with open(file) as fp:
        content = json.load(fp)
        assert content


def run():
    snippets_dir = Path(__file__).parent

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp = Path(tmp_dir_str)

        run_python_file(snippets_dir / 'formula_spotter.py', cwd=tmp)

        ttl = tmp / 'mathcheck.ttl'
        assert ttl.is_file()

        query = (snippets_dir / 'doc_query.sparql').read_text()

        graph = Graph()
        graph.parse(ttl, format='turtle')
        results = [str(row['document']) for row in graph.query(query)]
        assert results
        assert 'https://ns.mathhub.info/project/sb/data/test-corpus/paperA' in results

        run_shell_file(snippets_dir / 'preprocess.sh', cwd=tmp)

        run_python_file(snippets_dir / 'ext_decl_spotter.py', cwd=tmp)
        assert_nonempty_json_file(tmp / 'paper-A-annotations.json')

        run_shell_file(snippets_dir / 'normalize_selectors.sh', cwd=tmp)
        assert_nonempty_json_file(tmp / 'paper-A-annotations-normalized.json')

        run_python_file(snippets_dir / 'sblib_decl_spotter.py', cwd=tmp)
        run_shell_file(snippets_dir / 'anno_rdf_to_jsonld.sh', cwd=tmp)
        assert_nonempty_json_file(tmp / 'annotations.jsonld')

        (tmp / 'spotter.py').write_text((snippets_dir / 'spotter.py').read_text())
        run_shell_file(snippets_dir / 'run_spotter.sh', cwd=tmp)

        graph = rdflib.Graph()
        with gzip.open(tmp / 'spotterresults/example-decl-spotter.ttl.gz', 'rb') as fp:
            graph.parse(fp, format='turtle')

        assert len(graph) > 15


if __name__ == '__main__':
    run()
