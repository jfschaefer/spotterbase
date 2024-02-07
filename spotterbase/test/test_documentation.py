import doctest
import importlib.util
import unittest
from pathlib import Path


class TestDocumentation(unittest.TestCase):
    def test_examples(self):
        base = Path(__file__).parent.parent.parent
        doc_src = base / 'doc' / 'source'

        if not doc_src.is_dir():
            self.skipTest(f'Cannot test documentation examples ({doc_src} does not exist)')

        for path in doc_src.iterdir():
            if not (path.is_file() and path.name.endswith('.rst')):
                continue
            with self.subTest(file=str(path.relative_to(base))):
                doctest.testfile(str(path), module_relative=False)

        for path in doc_src.glob('snippets/**/snippet_test.py'):
            with self.subTest(file=str(path.relative_to(base))):
                spec = importlib.util.spec_from_file_location(path.parent.name + '_test', path)
                assert spec is not None
                module = importlib.util.module_from_spec(spec)
                assert spec.loader is not None
                spec.loader.exec_module(module)
                module.run()
