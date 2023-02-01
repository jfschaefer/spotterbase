import unittest

import rdflib
import rdflib.compare


class GraphTestMixin(unittest.TestCase):
    def assert_equal_graphs(self, got: rdflib.Graph, expected: rdflib.Graph):
        # note: using rdflib.compare.graph_diff instead of rdflib.compare.isomorphic to support debugging
        in_both, in_first, in_second = rdflib.compare.graph_diff(got, expected)
        # note: Displaying both in_first and in_second helps with debugging
        self.assertEqual(len(in_first) + len(in_second), 0,
                         f'''
The following triples were unexpected:
{in_first.serialize(format="nt")}

The following triples were missing:
{in_second.serialize(format="nt")}
'''.strip())
