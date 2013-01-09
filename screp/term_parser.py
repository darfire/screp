from pyparsing import (
        Word,
        Optional,
        Literal,
        Keyword,
        Forward,
        NoMatch,
        OneOrMore,
        ZeroOrMore,
        QuotedString,
        Group,
        )

from .actions import (
        make_pipe,
        make_action,
        )

def set_parser_results(res, value):
    res[0] = value

    del res[1:]

    return res


def any_of_keywords(kws):
    t = NoMatch()

    for k in kws:
        t = t ^ Keyword(k)

    return t


simple_accesors_kws = ['first', 'f', 'last', 'l', 'class', 'parent', 'p', 'text', 'tag']

simple_functions_kws = ['upper', 'lower', 'trim', 't']

anchor_kws = ['$', '@']

digits = '0123456789'

uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

lowers = uppers.lower()

attr_identifier = Word(lowers + uppers + '_')

quoted_string = QuotedString(quoteChar='\'', escChar='\\', escQuote='\\\'') ^\
        QuotedString(quoteChar='\"', escChar='\\', escQuote='\\\"')

natural_number = Word(digits).setParseAction(lambda s, l, t: [int(t[0])])

accessor_1_args = ((Keyword('children') + '(' + quoted_string + ')') ^\
        (any_of_keywords(['desc', 'd']) + '(' + quoted_string + ')') ^\
        (any_of_keywords(['nth', 'n']) + '(' + natural_number + ')') ^\
        (any_of_keywords(['attr', 'a']) + '[' + attr_identifier + ']'))

accessor_1_args.setParseAction(lambda s, l, t: set_parser_results(t, make_action(t[0], [t[2]])))

accessor_0_args = any_of_keywords(simple_accesors_kws).setParseAction(lambda s, l, t: set_parser_results(t, make_action(t[0])))

accessor = (accessor_0_args ^ accessor_1_args).setResultsName('accessors', listAllMatches=True)

accessors = OneOrMore(Literal('.').suppress() + accessor)

anchor = any_of_keywords(anchor_kws).setParseAction(lambda s, l, t: set_parser_results(t, make_action(t[0]))).setResultsName('anchor')

nonf_term = anchor + Optional(accessors)

func_term = Forward()

complex_function = NoMatch()

function_0_args = (any_of_keywords(simple_functions_kws) + '(' + func_term + ')').\
        setParseAction(lambda s, l, t: set_parser_results(t, make_action(t[0])))

f_term = (function_0_args ^ complex_function).setResultsName('functions', listAllMatches=True)

func_term << (f_term ^ nonf_term)

complex_filter = NoMatch()

filter_0_args = any_of_keywords(simple_functions_kws).setParseAction(lambda s, l, t: set_parser_results(t, make_action(t[0])))

any_filter = (filter_0_args ^ complex_filter).setResultsName('filters', listAllMatches=True)

filter_unit = Literal('|').suppress() + any_filter

filter_term = nonf_term + ZeroOrMore(filter_unit)

term = (func_term ^ filter_term)

term.setParseAction(lambda s, l, t: set_parser_results(t,
    make_pipe([t.get('anchor')] + list(t.get('accessors', [])) + list(t.get('functions', []) + list(t.get('filters', []))))))

curly_term = (Literal('{').suppress() + term + Literal('}').suppress()).setResultsName('terms', listAllMatches=True).setParseAction(lambda s, l, t: t[0])


class Location(object):
    pass


class ParsedTerm(object):
    def __init__(self, anchor, accessors, filters):
        self.anchor = anchor
        self.accessors = accessors
        self.filters = filters


class ParsedTermAction(object):
    def __init__(self, name, location, args=None):
        self.name = name
        if args is None:
            args = ()

        self.args = args

        self.location = location


    def __str__(self):
        return "ParsedTermAction<%s(%s) at %s>" % (self.name, ', '.join(self.args), self.location)


    __repr__ = __str__


class ParsedAnchor(object):
    def __init__(self, name, location):
        print name, location
        self.name = name
        self.location = location

digits = '0123456789'
uppers = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lowers = uppers.lower()
underscore = '_'

identifier_parser = Word(uppers + lowers + underscore, exact=1) + Optional(Word(uppers + lowers + digits + underscore), default='')

identifier_parser.addParseAction(lambda s, l, t: set_parser_results(t, t[0] + t[1]))

integer_parser = (Optional('-', default='') + Word(digits)).setParseAction(lambda s, l, t: set_parser_results(t, t[0] + t[1]))

quoted_string_parser = QuotedString(quoteChar='\'', escChar='\\', escQuote='\\\'') ^\
        QuotedString(quoteChar='\"', escChar='\\', escQuote='\\\"')


argument_parser = identifier_parser ^ integer_parser ^ quoted_string_parser

argument_list_parser = Literal('(').suppress() + argument_parser + ZeroOrMore(Literal(',').suppress() + argument_parser) + Literal(')').suppress()

action_parser = identifier_parser + Optional(Group(argument_list_parser), default=[])

action_parser.setParseAction(lambda s, l, t: set_parser_results(t, ParsedTermAction(t[0], l, args=t[1])))

filter_parser = Literal('|').suppress() + action_parser

accessor_parser = Literal('.').suppress() + action_parser

anchor_parser = (any_of_keywords(anchor_kws) ^ identifier_parser)

anchor_parser.addParseAction(lambda s, l, t: set_parser_results(t, ParsedAnchor(t[0], l)))

term_parser = anchor_parser + ZeroOrMore(accessor_parser) + ZeroOrMore(filter_parser)

term_parser.setParseAction(lambda s, l, t: set_parser_results(t, ParsedTerm(t[0], tuple(t[1]), tuple(t[2]))))

curly_term_parser = Literal('{').suppress() + term_parser + Literal('}').suppress()


if __name__ == '__main__':
    import sys

    for _ in  action_parser.scanString(sys.argv[1], maxMatches=1):
        print _


