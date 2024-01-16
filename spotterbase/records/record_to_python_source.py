"""Code for generating the code that makes a record.

This is used in the documentation to show how to create a record in code."""
import importlib
import itertools
from collections import defaultdict
from typing import Optional

from spotterbase.rdf import Uri
from spotterbase.records.record import Record


def record_to_python_source(record: Record) -> str:
    """Generate the code that makes a record.

    This is brittle and may not work for all records. It is intended for documentation purposes only."""
    symbols: dict[str, list[str]] = defaultdict(list)
    indent: int = 0
    lines: list[str] = []

    def require_symbol(class_: type):
        module = class_.__module__
        if module == 'builtins':
            return
        # try to import from parent module if possible
        while '.' in module:
            parent_module = importlib.import_module(module.rsplit('.', 1)[0])
            if hasattr(parent_module, class_.__name__) and getattr(parent_module, class_.__name__) is class_:
                module = parent_module.__name__
            else:
                break
        if class_.__name__ not in symbols[module]:
            symbols[module].append(class_.__name__)

    def stringify_value(val):
        require_symbol(type(val))
        r = repr(val)
        if r.startswith('datetime.datetime('):
            r = r[len('datetime.'):]
        return r

    def add_record(r: Record, name: Optional[str] = None):
        # Step 1: manage import
        class_ = type(r)
        require_symbol(class_)

        # Step 2: actually add the record to the lines
        nonlocal indent
        if name is None:
            lines.append(f'{indent * "    "}{class_.__name__}(')
        else:
            space = '' if indent else ' '
            lines.append(f'{indent * "    "}{name}{space}={space}{class_.__name__}(')
        indent += 1
        for attr in r.record_info.attrs:
            if not hasattr(r, attr.attr_name):
                continue
            val = getattr(r, attr.attr_name)
            if val is None:
                continue
            if attr.literal_type or isinstance(val, Uri):
                lines.append(f'{indent * "    "}{attr.attr_name}={stringify_value(val)},')
            elif isinstance(val, list):    # we do not support nested lists - should we?
                lines.append(f'{indent * "    "}{attr.attr_name}=[')
                indent += 1
                for item in val:
                    if isinstance(item, Record):
                        add_record(item)
                    else:
                        lines.append(f'{indent * "    "}{stringify_value(item)},')
                indent -= 1
                lines.append(f'{indent * "    "}],')
            elif isinstance(val, Record):
                add_record(val, attr.attr_name)
            else:
                raise ValueError(f'Unsupported type {type(val)} of {val!r}.')

        indent -= 1
        lines.append(f'{indent * "    "})' + (',' if indent else ''))

    snake_name = ''.join(
        ('_' if i and c.isupper() and n.islower() else '') + c.lower()
        for i, (c, n) in enumerate(itertools.pairwise(type(record).__name__))
    ) + type(record).__name__[-1].lower()

    add_record(record, snake_name)

    import_lines: list[str] = [
        'from ' + module + ' import ' + ', '.join(class_names)
        for module, class_names in symbols.items()
    ]

    complete_string = '\n'.join(import_lines) + '\n\n' + '\n'.join(lines)

    # print(complete_string)
    exec(complete_string)   # simple sanity check

    return complete_string
