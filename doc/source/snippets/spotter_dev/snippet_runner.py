"""This script runs all the snippets to ensure they are up-to-date."""

import tempfile
from pathlib import Path

from rdflib import Graph

from spotterbase.utils.snippet_runner_utils import run_python_file, run_shell_file

snippets_dir = Path(__file__).parent

with tempfile.TemporaryDirectory() as tmp_dir_str:
    tmp = Path(tmp_dir_str)

    run_python_file(snippets_dir / 'formula_spotter.py', cwd=tmp)

    ttl = tmp / 'mathcheck.ttl'
    assert ttl.is_file()
    # print(ttl.read_text())

    query = (snippets_dir / 'doc_query.sparql').read_text()

    graph = Graph()
    graph.parse(ttl, format='turtle')
    results = [str(row['document']) for row in graph.query(query)]
    assert results
    assert 'https://ns.mathhub.info/project/sb/data/test-corpus/paperA' in results

    run_shell_file(snippets_dir / 'preprocess.sh', cwd=tmp)
