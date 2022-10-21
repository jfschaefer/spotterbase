import enum
import json
import unicodedata
from dataclasses import dataclass
from typing import Union, Tuple, Optional, Any

from lxml.etree import _Element

import spotterbase.utils.xml_match as xm

to_superscript: dict[str, str] = {'-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                                  '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
from_superscript: dict[str, str] = {to_superscript[c]: c for c in to_superscript}


def superscript_int(integer: int) -> str:
    return ''.join(to_superscript[c] for c in str(integer))


class ScalarNotation(enum.IntFlag):
    SCIENTIFIC = enum.auto()  # scientific notation (x * 10^n)
    PLUS_MINUS = enum.auto()  # x ± ε
    DASH_RANGE = enum.auto()  # x - y
    TEXT_RANGE = enum.auto()  # x to y, between x and y
    IN_TEXT = enum.auto()  # at least one of the numbers is not in math mode
    IS_INT = enum.auto()  # 2.0 vs 2 may make a difference


@dataclass
class Scalars(object):
    # the main value (for simple ranges the start)
    value: float
    # the upper bound of a range
    range_upper: Optional[float] = None
    # the lower bound of ranges with a "main value" (e.g. in 5 ± 2)
    range_lower: Optional[float] = None
    scalar_notation: ScalarNotation = ScalarNotation(0)


@dataclass()
class Notation(object):
    # these kinds of optimizations might be necessary because we expect to have very many notations
    __slots__ = ['nodetype', 'attr', 'children', '_jsonstr']
    nodetype: str
    attr: dict[str, str]
    children: list['Notation']

    def __post_init__(self):
        n_children = {'i': 0, 'sup': 2, 'sub': 2, 'subsup': 3, 'seq': -1}
        assert self.nodetype in n_children
        assert len(self.children) == n_children[self.nodetype] or n_children[self.nodetype] == -1

        children = ', '.join(child.to_json() for child in self.children)
        attr = ', '.join(f'{json.dumps(key)}: {json.dumps(self.attr[key])}' for key in sorted(self.attr))
        self._jsonstr = f'[{json.dumps(self.nodetype)}, {{{attr}}}, [{children}]]'

    def to_json(self) -> str:
        """ Also serves as canonical string representation """
        return self._jsonstr

    @classmethod
    def from_json(cls, json_list) -> 'Notation':
        return Notation(json_list[0], json_list[1], [Notation.from_json(e) for e in json_list[3]])

    def __lt__(self, other: 'Notation') -> bool:
        return self.to_json() < other.to_json()


@dataclass
class UnitNotation(object):
    __slots__ = ['parts', '_jsonstr']
    parts: list[Tuple[Notation, int]]

    def __post_init__(self):
        # self.parts.sort()
        self._jsonstr = f'[{", ".join(f"[{notation.to_json()}, {exp}]" for notation, exp in self.parts)}]'

    def to_json(self) -> str:
        """ Also serves as canonical string representation """
        return self._jsonstr

    @classmethod
    def from_json(cls, json_list) -> 'UnitNotation':
        return UnitNotation([(Notation.from_json(notation), exp) for [notation, exp] in json_list])

    @classmethod
    def from_wikidata_string(cls, full_string: str) -> 'UnitNotation':
        string: str = full_string.strip()
        cur_id: str = ''
        in_denominator: bool = False
        exponent: str = ''
        parts: list[Tuple[Notation, int]] = []

        def push():
            nonlocal cur_id, parts, exponent
            if not cur_id:
                print('WARNING', repr(full_string), parts)
            e = int(exponent) if exponent else 1
            if in_denominator:
                e = -e
            attr = {'val': cur_id}
            #             if len(cur_id) == 1:
            #                 attr['mathvariant'] = 'normal'
            parts.append((Notation('i', attr, []), e))
            cur_id = ''
            exponent = ''

        for i, c in enumerate(string):
            if c in from_superscript:
                exponent += from_superscript[c]
            elif c.isspace():
                if string[i + 1] != '(':
                    push()
            elif c == '(':
                if in_denominator:
                    continue
                cur_id += c
            elif c == ')':
                if '(' in cur_id:
                    cur_id += c
                continue
            elif c == '/':
                push()
                in_denominator = True
            else:
                cur_id += c
        push()
        unit_notation = UnitNotation(parts)
        # print(full_string, unit_notation)
        return unit_notation

    def __hash__(self):
        return hash(self._jsonstr)

    def __eq__(self, other) -> bool:
        if not isinstance(other, UnitNotation):
            raise NotImplementedError()
        return self._jsonstr == other._jsonstr


class UndesirableMatchException(Exception):
    """
        A match cannot be processed or is rejected, even though it should be a valid match according to the matcher.
        You could say it's a logical error, not a syntax error.
    """
    pass


# ***************
# * BASIC NODES *
# ***************

mrow = xm.tag('mrow')
mo = xm.tag('mo')
mn = xm.tag('mn')
mtext = xm.tag('mtext')
msup = xm.tag('msup')

relational_mo = mo.with_text(
    '[' + ''.join({'=', '≈', '<', '>', '≪', '≫', '≥', '⩾', '≤', '⩽', '∼', '≲', '≳'}) + ']')
empty_tag = xm.any_tag.with_text('^$')
space = mtext.with_text(r'\s*')
base = xm.tag('math') / xm.tag('semantics')


# ***********************
# * NUMBERS AND SCALARS *
# ***********************

def mn_to_number(mn_text: Optional[str]) -> Union[float, int]:
    assert mn_text
    reduced = ''
    for c in mn_text:
        if c.isnumeric():
            reduced += c
        elif c == '.':
            reduced += c
        elif c.isspace():
            continue
        else:
            print(f'Can\'t convert mn {repr(mn_text)}')
    return float(reduced) if '.' in reduced else int(reduced)


simple_number = (
                        mn ** 'numeral' |
                        mrow / xm.seq(mo.with_text(r'[-–]') ** 'negative', mn ** 'numeral')
                ) ** 'simplenumber'
power_of_10 = (msup / xm.seq(mn.with_text('^10$'), simple_number ** 'exponent')) ** 'powerof10'
scientific_number = (mrow / xm.seq(simple_number ** 'factor', mtext.with_text('[×]'),
                                   power_of_10)) ** 'scientific'


def tree_to_number(lt: xm.MatchTree) -> Tuple[Union[int, float], str]:
    if lt.label == 'simplenumber':
        sign = -1 if 'negative' in lt else 1
        assert lt['numeral'].node is not None
        return sign * mn_to_number(lt['numeral'].node.text), 'simple'
    elif lt.label == 'scientific':
        return tree_to_number(lt['factor'])[0] * tree_to_number(lt['powerof10'])[0], 'scientific'
    elif lt.label == 'powerof10':
        return 10 ** tree_to_number(lt['exponent'])[0], 'powerof10'
    elif len(lt.children) == 1:
        return tree_to_number(lt.children[0])
    raise Exception(f'Unsupported tree: {lt}')


scalar = (simple_number | scientific_number | power_of_10 |
          (mrow / xm.seq(empty_tag, mo.with_text(f'^{unicodedata.lookup("INVISIBLE TIMES")}$'),
                         power_of_10))  # presumably this happens when using siunitx and leaving the factor empty
          ) ** 'scalar'


def scalar_to_scalars(lt: xm.MatchTree) -> Scalars:
    number, type_ = tree_to_number(lt)
    scalar_notation = ScalarNotation(0)
    if type(number) == int:
        scalar_notation |= ScalarNotation.IS_INT
    if type_ == 'scientific':
        scalar_notation |= ScalarNotation.SCIENTIFIC
    return Scalars(float(number), scalar_notation=scalar_notation)


# ***********
# * SYMBOLS *
# ***********

simple_symbol = xm.tag('mi') | xm.tag('mo')
complex_symbol = (
        (xm.tag('msub') / xm.seq(simple_symbol, xm.any_tag)) |
        (xm.tag('msup') / xm.seq(simple_symbol, xm.any_tag)) |
        (xm.tag('msubsup') / xm.seq(simple_symbol, xm.any_tag, xm.any_tag))
)
symbol = simple_symbol | complex_symbol


def symbol_to_notation(node: _Element) -> Notation:
    # TODO: Invisible characters?
    if node.tag in {'mi', 'mn', 'mo'}:
        attr: dict[str, Any] = {'val': node.text}
        if node.tag == 'mi' and node.text and len(node.text) == 1 and node.get('mathvariant') != 'normal':
            attr['isitalic'] = True
        return Notation('i', attr, [])
    elif node.tag in {'msup', 'msub', 'msubsup'}:
        return Notation(node.tag[1:], {}, [symbol_to_notation(child) for child in node.iterchildren()])
    elif node.tag == 'mrow':
        # TODO: We need some kind of normalization (merge consecutive identifiers etc.)
        return Notation('seq', {}, [symbol_to_notation(child) for child in node.iterchildren()])
    raise Exception('Unsupported symbol node: ' + node.tag)


# *********
# * UNITS *
# *********

simple_unit = (simple_symbol | (xm.tag('msub') / xm.seq(simple_symbol, xm.any_tag))) ** 'simpleunit'


# simple_unit = simple_symbol ** 'simpleunit'


def simple_unit_to_notation(lt: xm.MatchTree) -> Notation:
    assert lt.label == 'simpleunit'
    # TODO: This will get much more complex
    assert (node := lt.node) is not None
    return symbol_to_notation(node)


unit_power = (xm.tag('msup') / xm.seq(simple_unit, simple_number ** 'exponent')) ** 'unitpower'
unit_times2 = (mrow / xm.seq(simple_unit | unit_power, xm.maybe(space), simple_unit | unit_power)) ** 'unittimes'
unit_times3 = (mrow / xm.seq(simple_unit | unit_power, xm.maybe(space), simple_unit | unit_power, xm.maybe(space),
                             simple_unit | unit_power)) ** 'unittimes'
unit = (simple_unit | unit_power | unit_times2 | unit_times3) ** 'unit'


def unit_to_unit_notation(lt: xm.MatchTree) -> UnitNotation:
    if lt.label == 'unit':
        assert len(lt.children) == 1
        return unit_to_unit_notation(lt.children[0])
    elif lt.label == 'simpleunit':
        notation = simple_unit_to_notation(lt)
        return UnitNotation([(notation, 1)])
    elif lt.label == 'unitpower':
        notation = simple_unit_to_notation(lt['simpleunit'])
        exponent = tree_to_number(lt['exponent'])[0]
        if exponent not in range(-10, 10) or not isinstance(exponent, int):
            raise UndesirableMatchException(f'Bad exponent for a unit: {exponent}')
        return UnitNotation([(notation, exponent)])
    elif lt.label == 'unittimes':
        parts = []
        for subunit in lt.children:
            parts += unit_to_unit_notation(subunit).parts
        return UnitNotation(parts)
    raise Exception(f'Unsupported node: {lt.label}')


# **************
# * QUANTITIES *
# **************

quantity = mrow / xm.seq(scalar, xm.maybe(space), unit)
quantity_in_rel = mrow / xm.seq(xm.maybe(xm.any_tag), relational_mo, quantity)
