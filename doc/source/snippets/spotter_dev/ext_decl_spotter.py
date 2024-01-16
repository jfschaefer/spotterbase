import json
import re

with open('preprocessed-paper-A.json') as fp:
    document = json.load(fp)

decl_regex = re.compile(r'(for all|for every|for any|where|let) (?P<formula>@MathNode:(\d+)@)')
