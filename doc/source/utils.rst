:mod:`~spotterbase.utils` package
====================================

The :mod:`spotterbase.utils` provides various tools that
may be helpful for the development of spotters.


The :mod:`~spotterbase.utils.xml_match` module
----------------------------------------------

Background
""""""""""

Many spotters need to find XML nodes that follow a particular pattern.
As a running example, we will look for presentation MathML
that corresponds to expressions of the form :math:`r\times 10^n`,
like :math:`5.3\times 10^{-2}`,
which would have the following presentation MathML:

.. code:: XML

   <mrow>
     <mn>5.3</mn>
     <mo>×</mo>
     <msup>
       <mn>10</mn>
       <mrow>
         <mo>-</mo>
         <mn>2</mn>
       </mrow>
     </msup>
   </mrow>

Developing an XPath expression would be rather difficult and
the goal of this module is to make the whole thing easier and more modular.

My instinct is that this should be a common problem
and that there should be well-established solutions for this.
I just haven't found any.
Note that computer linguists face a similar problem when
working with natural language parse trees
(but I haven't found any tools that could be easily used).
That being said, I was not particularly patient with my search.


Matching simple nodes
"""""""""""""""""""""

Imports and loading the example XML tree::

    >>> from lxml import etree
    >>> import spotterbase.utils.xml_match as xm

Let's match simple numbers::

    >>> mn_42 = etree.fromstring('<mn>42</mn>')
    >>> nat_matcher = xm.tag('mn').with_text('[0-9]+') ** 'nat'
    >>> list(nat_matcher.match(mn_42))
    [<"nat">]

There is a lot to unpack here:
1. ``mn_42`` is just an example XML tree.
2. ``nat_matcher`` is a matcher for XML trees that correspond natural numbers:

    * ``xm.tag('mn')`` gives us a simple matcher for ``<mn>`` nodes.
    * ``.with_text('[0-9]+')`` restricts the matcher to only match nodes
        whose text content matches the regular expression ``[0-9]+``.
    * ``** 'nat'`` adds a label to the match.
        The idea is similar to named groups in Python's regular expressions.
        Tags only really make sense with more complex examples.

3. ``nat_matcher.match(mn_42)`` returns an iterator for all matches in ``mn42`` (in this case only one).
    You can ignore the output for now.

Currently, we cannot match floating point numbers, but of course we can make a new matcher::

    >>> mn_pi = etree.fromstring('<mn>3.14159</mn>')
    >>> list(nat_matcher.match(mn_pi))
    []
    >>> float_matcher = xm.tag('mn').with_text(r'[0-9]*\.[0-9]*') ** 'float'
    >>> list(float_matcher.match(mn_pi))
    [<"float">]
    >>> list(float_matcher.match(mn_42))   # doesn't have a decimal point
    []


Union of matchers
"""""""""""""""""

If we want to match both floats and natural numbers, we can take the
union of the matchers::

    >>> combined_matcher = nat_matcher | float_matcher
    >>> list(combined_matcher.match(mn_pi))
    [<"float">]
    >>> list(combined_matcher.match(mn_42))
    [<"nat">]


Looking deeper
""""""""""""""

Negative numbers have a more complex MathML representation,
which requires us to look at descendents of nodes as well::

    >>> neg_42 = etree.fromstring('<mrow><mo>-</mo><mn>42</mn></mrow>')
    >>> neg_int_matcher = xm.tag('mrow') ** 'negint' / xm.seq(xm.tag('mo').with_text('-'), nat_matcher)
    >>> list(neg_int_matcher.match(neg_42))
    [<"negint": <"nat">>]

``xm.seq(a, b)`` creates creates a sequence matcher, which matches any sequence
where the beginning matches ``a`` and the rest matches ``b``. Longer sequences are also possible.
In the example above, ``neg_int_matcher`` matches any ``<mrow>`` node that has exactly two children:
an ``<mo>`` with text ``-``, followed by a natural number.

The matches are :class:`~spotterbase.utils.xml_match.MatchTree` objects.
We will take a closer look at them later on.
But to give you a first impression::

    >>> match_tree = next(neg_int_matcher.match(neg_42))  # get first match
    >>> match_tree
    <"negint": <"nat">>
    >>> match_tree["nat"]     # the "nat" submatch is also a MatchTree
    <"nat">
    >>> match_tree["nat"].node.text   # we can get the tagged lxml nodes
    '42'


Matching scientific number notation
"""""""""""""""""""""""""""""""""""

For illustration, let us develop a matcher for the example from above::

    >>> ten_matcher = xm.tag('mn').with_text('10')
    >>> int_matcher = nat_matcher | neg_int_matcher
    >>> sci_matcher = xm.tag('mrow') ** 'sci_not' / xm.seq(
    ...     combined_matcher ** 'factor',     # float or natural number
    ...     xm.tag('mo').with_text('[×⋅]'),   # multiplication operator
    ...     xm.tag('msup') / xm.seq(ten_matcher, int_matcher**'exponent')
    ... )
    >>> tree = etree.fromstring('''<mrow><mn>5.3</mn><mo>×</mo><msup><mn>10</mn><mrow><mo>-</mo><mn>2</mn></mrow></msup></mrow>''')
    >>> list(sci_matcher.match(tree))
    [<"sci_not": <"factor": <"float">, "exponent": <"negint": <"nat">>>>]


Working with the :class:`~spotterbase.utils.xml_match.MatchTree`
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Every match tree has a label, an associated lxml node and possible one or more children,
which are again match trees.
We can use this implement a converter function, that takes a match tree as described above
and converts it to a Python number::

    >>> def convert(match_tree):
    ...     if match_tree.label == 'sci_not':
    ...         return convert(match_tree['factor']) * 10 ** convert(match_tree['exponent'])
    ...     elif match_tree.label == 'float':
    ...         return float(match_tree.node.text)
    ...     elif match_tree.label == 'nat':
    ...         return int(match_tree.node.text)
    ...     elif match_tree.label == 'negint':
    ...         return -convert(match_tree['nat'])
    ...     elif match_tree.label in {'factor', 'exponent'}:
    ...         return convert(match_tree.only_child)
    ...     else:
    ...         raise NotImplementedError(f'Unexpected label: "{match_tree.label}"')
    >>> match_tree = next(sci_matcher.match(tree))  # first match
    >>> convert(match_tree)
    0.053

