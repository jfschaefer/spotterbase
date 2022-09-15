import pathlib
import unittest

loader = unittest.TestLoader()
suite = loader.discover(str(pathlib.Path(__file__).parent))
runner = unittest.TextTestRunner()
runner.run(suite)



