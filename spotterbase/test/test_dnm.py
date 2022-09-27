import unittest
import io

from lxml import etree

from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import SimpleTokenGenerator


class TestDnm(unittest.TestCase):
    def test_basic(self):
        html = '<a>t1<b class="standard">t2</b>t3<c/>t4<d class="skip">D</d>t5</a>'
        tree = etree.parse(io.StringIO(html))
        dnm = TokenBasedDnm.from_token_generator(tree,
                                                 SimpleTokenGenerator(nodes_to_replace={'c': 'C'},
                                                                      classes_to_replace={'skip': ''}))
        dnmstr = dnm.get_dnm_str()
        self.assertEqual(dnmstr, 't1t2t3Ct4t5')
