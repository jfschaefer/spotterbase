from lxml import etree
import lxml.html

from spotterbase.dnm.token_dnm import TokenBasedDnm
from spotterbase.dnm.token_generator import DefaultGenerators

tree = lxml.html.parse('1910.06709.html')


dnm = TokenBasedDnm.from_token_generator(tree, DefaultGenerators.ARXMLIV_TEXT_ONLY)

dnm_str = dnm.get_dnm_str()

print(dnm_str[2900:3000])

# dnm_str[2910:2913] belongs to a math node

math_node = dnm_str[2910:2913].as_range().to_dom().from_.node

print(etree.tostring(math_node))
