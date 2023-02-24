import doctest
import unittest
from pathlib import Path


class TestDocumentation(unittest.TestCase):
    def test_examples(self):
        base = Path(__file__).parent.parent.parent
        for path in (base / 'doc' / 'source').iterdir():
            if not (path.is_file() and path.name.endswith('.rst')):
                continue
            with self.subTest(file=str(path.relative_to(base))):
                doctest.testfile(str(path), module_relative=False, raise_on_error=True)
