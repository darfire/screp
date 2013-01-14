import pytest
import lxml.etree as etree
from lxml.cssselect import CSSSelector

def el(string):
    return etree.fromstring(string)


def generate_parent_success_cases(cases):
    def process(elstr, elsel, parsel):
        root = el(elstr)

        kid = CSSSelector(elsel)(root)[0]

        if parsel is not None:
            parent = CSSSelector(parsel)(root)[0]
        else:
            parent = None

        return (kid, (), parent)

    return map(lambda x: process(*x), cases)

scenarios = [
        {
            # first
            'names': ('f', 'first'),
            'success_cases': [
                ([1], (), 1),
                (['a', 'b', 'c'], (), 'a'),
                ],
            'execution_failure_cases': [
                ([], (), IndexError),
                ([1], (2,),  TypeError),
                (1, (), TypeError),
                ],
            'creation_failure_cases': [
                ],
            },
        {
            # last
            'names': ('l', 'last'),
            'success_cases': [
                ([1], (), 1),
                (['a', 'b', 'c'], (), 'c'),
                ],
            'execution_failure_cases': [
                ([], (), IndexError),
                ([1], (2,), TypeError),
                (1, (), TypeError),
                ],
            'creation_failure_cases': []
            },
        {
            # nth
            'names': ('nth', 'n'),
            'success_cases': [
                ([1, 2, 3], (1,), 2),
                ([1, 2, 3, 4], (-1,), 4),
                ([1, 2, 3, 4], (0,), 1),
                ],
            'execution_failure_cases': [
                ([1, 2], (2,), IndexError),
                ([], (0,), IndexError),
                ([], (-1,), IndexError),
                ([1, 2, 3], (-4,), IndexError),
                (12, (0,), TypeError),
                ([1, 2, 3], (), TypeError),
                ([1, 2, 3], (1, 2), TypeError),
                ],
            'creation_failure_cases': []
            },
        {
            # upper
            'names': ('upper',),
            'success_cases': [
                ('abc', (), 'ABC'),
                (' a1b2c', (), ' A1B2C'),
                (' a1B2c', (), ' A1B2C'),
                (' 123&*', (), ' 123&*'),
                ('', (), ''),
                ],
            'execution_failure_cases': [
                ('abc', (1,), TypeError),
                ([], (), AttributeError),
                (1, (), AttributeError),
                ],
            'creation_failure_cases': []
            },
        {
            # lower
            'names': ('lower',),
            'success_cases': [
                ('ABC', (), 'abc'),
                (' A1B2C', (), ' a1b2c'),
                (' A1b2C', (), ' a1b2c'),
                (' 123&*', (), ' 123&*'),
                ('', (), ''),
                ],
            'execution_failure_cases': [
                ('AbC', (1,), TypeError),
                ([], (), AttributeError),
                (1, (), AttributeError),
                ],
            'creation_failure_cases': []
            },
        {
            # trim
            'names': ('trim', 't'),
            'success_cases': [
                ('ab123', (), 'ab123'),
                (' abc', (), 'abc'),
                (' abc ', (), 'abc'),
                ('\tabc  ', (), 'abc'),
                ('  ab  cd   ', (), 'ab  cd'),
                ('', (), ''),
                ],
            'execution_failure_cases': [
                (' AbC ', (1,), TypeError),
                ([], (), AttributeError),
                (1, (), AttributeError),
                ],
            'creation_failure_cases': []
            },
        {
            # class
            'names': ('class',),
            'success_cases': [
                (el('<div class="C1" a1="1"></div>'), (), 'C1'),
                ],
            'execution_failure_cases': [
                (el('<div/>'), (1,), TypeError),
                (1, (), AttributeError),
                ('123', (), AttributeError),
                ([el('<div class="cls"/>'), el('<p class="cls"/>')], (), AttributeError),
                (el('<tag class_="cls"></tag>'), (), KeyError),
                (el('<p>text</p>'), (), KeyError),
                ],
            'creation_failure_cases': []
            },
        {
            # id
            'names': ('id',),
            'success_cases': [
                (el('<div id="I1" a1="1"></div>'), (), 'I1'),
                ],
            'execution_failure_cases': [
                (el('<div/>'), (1,), TypeError),
                (1, (), AttributeError),
                ('123', (), AttributeError),
                ([el('<div id="id"/>'), el('<p id="id"/>')], (), AttributeError),
                (el('<tag id_="id"></tag>'), (), KeyError),
                (el('<p>text</p>'), (), KeyError),
                ],
            'creation_failure_cases': []
            },
        {
            # tag
            'names': ('tag',),
            'success_cases': [
                (el('<tag/>'), (), 'tag'),
                (el('<div class="cls">text</div>'), (), 'div'),
                (el('<p id="pid"/>'), (), 'p'),
                ],
            'execution_failure_cases': [
                (el('<div/>'), (1,), TypeError),
                (1, (), AttributeError),
                ('123', (), AttributeError),
                ([el('<div id="id"/>'), el('<p id="id"/>')], (), AttributeError),
                ],
            'creation_failure_cases': [],
            },
        {
            # text
            'names': ('text',),
            'success_cases': [
                (el('<tag/>'), (), None),
                (el('<tag></tag>'), (), None),
                (el('<div class="cls">text</div>'), (), 'text'),
                (el('<p>one\ntwo</p>'), (), 'one\ntwo'),
                ],
            'execution_failure_cases': [
                (el('<div/>'), (1,), TypeError),
                (1, (), AttributeError),
                ('123', (), AttributeError),
                ([el('<div id="id"/>'), el('<p id="id"/>')], (), AttributeError),
                ],
            'creation_failure_cases': [],
            },
        {
            # attr
            'names': ('attr', 'a'),
            'success_cases': [
                (el('<tag attr="v1" class="c1"/>'), ('attr',), 'v1'),
                (el('<tag a1="v1" a2="va lue">text</tag>'), ('a2',), 'va lue'),
                ],
            'execution_failure_cases': [
                (el('<div/>'), (1,), TypeError),
                (el('<div/>'), ([1, 2, 3],), TypeError),
                (1, ('attr',), AttributeError),
                ('123', ('attr',), AttributeError),
                ([el('<div id="id"/>'), el('<p id="id"/>')], (), Exception),
                (el('<tag a1="v1"/>'), ('a2',), KeyError),
                ],
            'creation_failure_cases': [],
            },
        {
            # parent
            'names': ('parent', 'p'),
            'success_cases': generate_parent_success_cases([
                ('<div class="c1"><p>text</p></div>', 'p', '.c1'),
                ('<div class="c1"><div class="c2"/></div>', '.c2', '.c1'),
                ('<t1><t2/></t1>', 't2', 't1'),
                ]),
            'execution_failure_cases': [
                (el('<div/>'), (1,), TypeError),
                (el('<div/>'), ([1, 2, 3],), TypeError),
                (1, ('attr',), TypeError),
                ('123', ('attr',), TypeError),
                ([el('<div id="id"/>'), el('<p id="id"/>')], (), Exception),
                (el('<t1><t2/></t1>'), (), Exception),
                ],
            'creation_failure_cases': [],
            },
        {
            # desc
            'names': ('desc', 'd'),
            # TODO
            },
        {
            # fdesc
            'names': ('fdesc', 'fd'),
            # TODO
            },
        ]


def generate_success_scenarios():
    for s in scenarios:
        for n in s['names']:
            for sc in s.get('success_cases', []):
                yield (n, sc[1], sc[0], sc[2])


def generate_execution_failure_scenarios():
    for s in scenarios:
        for n in s['names']:
            for sc in s.get('execution_failure_cases', []):
                    yield (n, sc[1], sc[0], sc[2])


def generate_creation_failure_scenarios():
    for s in scenarios:
        for n in s['names']:
            for sc in s.get('creation_failure_cases', []):
                    yield (n, sc[0], sc[1])


scenario_generators = {
        'test_action_success': (('name', 'args', 'in_value', 'out_value'), generate_success_scenarios),
        'test_action_execution_failure': (('name', 'args', 'in_value', 'exception_class'), generate_execution_failure_scenarios),
        'test_action_creation_failure': (('name', 'args', 'exception_class'), generate_creation_failure_scenarios),
        }


def pytest_generate_tests(metafunc):
    fname = metafunc.function.__name__

    argnames = scenario_generators[fname][0]
    generator = scenario_generators[fname][1]

    metafunc.parametrize(argnames, list(generator()))


def test_action_success(name, args, in_value, out_value):
    import screp.actions as actions
    import screp.term_parser as parsers

    parsed_action = parsers.ParsedTermAction(name, 0, args=args)

    action = actions.make_action(parsed_action)

    assert action.execute(in_value) == out_value


def test_action_execution_failure(name, args, in_value, exception_class):
    import screp.actions as actions
    import screp.term_parser as parsers

    parsed_action = parsers.ParsedTermAction(name, 0, args=args)

    action = actions.make_action(parsed_action)

    with pytest.raises(exception_class):
        action.execute(in_value)


def test_action_creation_failure(name, args, exception_class):
    import screp.actions as actions
    import screp.term_parser as parsers

    parsed_action = parsers.ParsedTermAction(name, 0, args=args)

    with pytest.raises(exception_class):
        action = actions.make_action(parsed_action)

