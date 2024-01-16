import doctest
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
