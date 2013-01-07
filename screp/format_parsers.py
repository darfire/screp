from pyparsing import (
        Literal,
        ZeroOrMore,
        StringEnd,
        )

from .term_parser import curly_term
from .formatter import CSVFormatter

comma = Literal(',').suppress()

csv_format = curly_term + ZeroOrMore(comma + curly_term) + StringEnd()

def parse_csv_formatter(value):
    result = csv_format.parseString(value)

    terms = result.get('terms')

    return (CSVFormatter(len(terms)), terms)


if __name__ == '__main__':
    import sys

    print parse_csv_formatter(sys.argv[1])
