from pyparsing import (
        Literal,
        ZeroOrMore,
        StringEnd,
        )
import re

from .term_parser import curly_term_parser, parse_term
from .actions import make_term, make_anchor
from .formatter import CSVFormatter

comma = Literal(',').suppress()

csv_format_parser = curly_term_parser + ZeroOrMore(comma + curly_term_parser) + StringEnd()


def parse_csv_formatter(value, header=None):
    result = csv_format_parser.parseString(value)

    terms = map(make_term, result)

    return (CSVFormatter(len(terms), header=header), terms)


anchor_re = re.compile('^(?P<name>[_A-Za-z][_A-Za-z0-9]*)\s*=(?P<term_spec>.*)$')


def parse_anchor(string):
    m = anchor_re.match(string)
    if m is None:
        raise ValueError('Invalid anchor format')

    name = m.group('name')

    try:
        pterm = parse_term(m.group('term_spec'))
    except Exception as e:
        raise ValueError("Anchor '%s': %s" % (name, e))

    return make_anchor(name, pterm)


if __name__ == '__main__':
    import sys

    print parse_csv_formatter(sys.argv[1])
