import os
import sys
import unittest

if sys.version_info < (3, 10):
    print('SpotterBase is only tested with Python 3.10 or higher.', file=sys.stderr)
    print(f'You seem to be running Python version {sys.version.split()[0]}', file=sys.stderr)

loader = unittest.TestLoader()
suite = loader.discover(os.path.dirname(__file__))
runner = unittest.TextTestRunner()
runner.run(suite)
