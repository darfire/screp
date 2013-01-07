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


if __name__ == '__main__':
    import sys

    results = term.parseString(sys.argv[1])

    print results, results.keys(), results.get('anchor'), results.get('filters', []), results.get('functions', []), results.get('accessors')
