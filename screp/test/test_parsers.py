import pytest

# accessor_parser tests
# TODO: implement this


# action_parser tests
class TestActionParser(object):
    matches = [
            ('a(1, 2, 3, 4)', ('a', ('1', '2', '3', '4')), ''),
            ('_abc', ('_abc', ()), ''),
            (' \tid(1, 2, "abc \\"12") tail', ('id', ('1', '2', 'abc "12')), ' tail'),
            ('name tail', ('name', ()), ' tail'),
            (' name (_arg)', ('name', ('_arg',)), ''),
            ('name()', ('name', ()), '()'),
            (' name (1,, 2, 3)', ('name', ()), ' (1,, 2, 3)'),
            ('\tf tail', ('f', ()), ' tail'),
            ]


    non_matches = [
            (' 1name',),
            ]

    @staticmethod
    def check_action(action, name, extras):
        import screp.term_parser as module
        import screp.idloc as idloc

        assert type(action) == module.ParsedTermAction
        assert action.name == name and tuple(action.args) == tuple(extras)
        assert type(action.identification) == idloc.Identification


    @pytest.mark.parametrize(('string', 'match', 'tail'), matches)
    def test_matches(self, string, match, tail):
        import screp.term_parser as module
        # if we have tabs, don't expand them
        module.action_parser.parseWithTabs()
        (ret, s, e) = module.action_parser.scanString(string, maxMatches=1).next()

        TestActionParser.check_action(ret[0], *match)

        # HACK: stripping tails, ignoring spaces
        assert string[e:].strip() == tail.strip()


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.action_parser.parseString(string)


# filter_parser tests
class TestFilterParser(object):
    hchar = '|'

    matches = [
            ('  |a(1, 2,3) tail', ('a', ('1', '2', '3')), ' tail'),
            ('| name| tail', ('name', ()), '| tail'),
            ('  |name (1, 2, ', ('name', ()), ' (1, 2, '),
            ('\t|name (1, 2, 3) tail', ('name', ('1', '2', '3')), ' tail'),
            ]

    no_matches = [
            ('| ',),
            ('name(a, b, c)',),
            ('. name(a, b, c)',),
            ]


    @pytest.mark.parametrize(('string', 'match', 'tail'),
            map(lambda x: (' | ' + x[0], x[1], x[2]), TestActionParser.matches) + matches)
    def test_matches(self, string, match, tail):
        import screp.term_parser as module
        # if we have tabs, don't expand them
        module.filter_parser.parseWithTabs()
        (ret, s, e) = module.filter_parser.scanString(string, maxMatches=1).next()

        TestActionParser.check_action(ret[0], *match)

        # HACK: stripping tails, ignoring spaces
        assert string[e:].strip() == tail.strip()


    @pytest.mark.parametrize(('string',), no_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.filter_parser.parseString(string)


# quoted_string_parser tests
class TestQuotedStringParser(object):
    matches = [
        (' "123 asda a" tail', '123 asda a', ' tail'),
        ('"123 \\" asda"', '123 " asda', ''),
        ('    "abc \\\\\\" xyz"', 'abc \\" xyz', ''),
        ('"abc \\\\" xyz"', 'abc \\\\', ' xyz"'),

        (" '123 asda a' tail", '123 asda a', ' tail'),
        ("'123 \\' asda'", "123 ' asda", ''),
        ("    'abc \\\\\\' xyz'", "abc \\' xyz", ''),
        ("'abc \\\\' xyz'", 'abc \\\\', " xyz'"),

        ('"123\'345"', '123\'345', ''),
        ('"123\\\'345"', '123\\\'345', ''),
        ]

    non_matches = [
        ('',),
        ('123',),
        ('"123 ',),
        ('"123 \\"',),
        ('"123 \'',),
        ("'123 \"",),
        ("'123 \\'",),
        ('123"',),
        ("123'",),
        ]
    @pytest.mark.parametrize(('string', 'match', 'tail'), matches)
    def test_matches(self, string, match, tail):
        import screp.term_parser as module
        (ret, s, e) = module.quoted_string_parser.scanString(string, maxMatches=1).next()

        assert ret[0] == match and string[e:] == tail


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.quoted_string_parser.parseString(string)


# integer_parser tests
class TestIntegerParser(object):
    matches = [
        ('121', '121', ''),
        (' 121', '121', ''),
        ('\t121 tail', '121', ' tail'),
        (' 231 tail', '231', ' tail'),
        ('0121', '0121', ''),
        (' 000012400', '000012400', ''),
        ('112-121', '112', '-121'),
        ('989a345', '989', 'a345'),
        ('-45abc', '-45', 'abc'),
        (' -74', '-74', ''),
        ]

    non_matches = [
        ('a123',),
        ('',),
        ('_123',),
        ('.123',),
        ('-a123',),
        ]
    @pytest.mark.parametrize(('string', 'integer', 'tail'), matches)
    def test_matches(self, string, integer, tail):
        import screp.term_parser as module
        module.integer_parser.parseWithTabs()
        (ret, s, e) = module.integer_parser.scanString(string, maxMatches=1).next()

        assert ret[0] == integer and string[e:] == tail


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.integer_parser.parseString(string)


# identifier_parser tests
class TestIdentifierParser(object):
    matches = [
                ('id tail', 'id', ' tail'),
                ('i1d', 'i1d', ''),
                ('id1', 'id1', ''),
                ('_id', '_id', ''),
                ('i_d', 'i_d', ''),
                ('id_', 'id_', ''),
                ('ID', 'ID', ''),
                ('iD', 'iD', ''),
                (' id', 'id', ''),
                ('i', 'i', ''),
                ('i d', 'i', ' d'),
                ]

    non_matches = [
                ('.id',),
                ('1id',),
                (' 1id',),
                (' ~id',),
                ('',),
                ]

    @pytest.mark.parametrize(('string', 'identifier', 'tail'), matches)
    def test_matches(self, string, identifier, tail):
        import screp.term_parser as module
        (ret, s, e) = module.identifier_parser.scanString(string, maxMatches=1).next()

        assert ret[0] == identifier and string[e:] == tail


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.identifier_parser.parseString(string)


# argument_parser tests
class TestArgumentParser(object):
    non_matches = [
            ('.id',),
            (' ~id',),
            ('',),
            ('.123',),
            ('-a123',),
            ('"123 ',),
            ('"123 \\"',),
            ('"123 \'',),
            ("'123 \"",),
            ("'123 \\'",),
            ]

    @pytest.mark.parametrize(('string',), map(lambda x: (x[0],), TestIntegerParser.matches))
    def test_integers(self, string):
        import screp.term_parser as module

        r1 = module.argument_parser.parseString(string)

        r2 = module.integer_parser.parseString(string)

        assert r1[0] == r2[0]


    @pytest.mark.parametrize(('string',), map(lambda x: (x[0],), TestIdentifierParser.matches))
    def test_identifiers(self, string):
        import screp.term_parser as module
        r1 = module.argument_parser.parseString(string)

        r2 = module.identifier_parser.parseString(string)

        assert r1[0] == r2[0]


    @pytest.mark.parametrize(('string',), map(lambda x: (x[0],), TestQuotedStringParser.matches))
    def test_quoted_strings(self, string):
        import screp.term_parser as module
        r1 = module.argument_parser.parseString(string)

        r2 = module.quoted_string_parser.parseString(string)

        assert r1[0] == r2[0]


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.argument_parser.parseString(string)


# argument_list_parser tests
class TestArgumentListParser(object):
    matches = [
            ('(1, 2, 3, 4) tail', ('1', '2', '3', '4'), ' tail'),
            # TODO: more here
            ]

    non_matches = [
            ('1, 2, 3)',),
            ('(1, 2,',),
            ('(1,, 2)',),
            ('((1, 2, 3)',),
            ('(, 1, 2)',),
            ('(1, 2, (3, 4))',),
            ]
           

    @pytest.mark.parametrize(('string', 'match', 'tail'), matches)
    def test_matches(self, string, match, tail):
        import screp.term_parser as module

        (ret, s, e) = module.argument_list_parser.scanString(string, maxMatches=1).next()

        assert tuple(ret) == match and string[e:] == tail


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.argument_list_parser.parseString(string)


# anchor_parser tests
class TestAnchorParser(object):
    matches = [
            ('$', '$', ''),
            ('  $ tail', '$', ' tail'),
            ('@', '@', ''),
            (' @   tail', '@', '   tail'),
            ]

    @staticmethod
    def check_anchor(anchor, name):
        import screp.term_parser as module
        import screp.idloc as idloc

        assert type(anchor) == module.ParsedAnchor
        assert anchor.name == name
        assert type(anchor.identification) is idloc.Identification

    @pytest.mark.parametrize(('string', 'match', 'tail'), TestIdentifierParser.matches + matches)
    def test_matches(self, string, match, tail):
        import screp.term_parser as module
        (ret, s, e) = module.anchor_parser.scanString(string, maxMatches=1).next()

        TestAnchorParser.check_anchor(ret[0], match)

        assert string[e:].strip() == tail.strip()


    @pytest.mark.parametrize(('string',), TestIdentifierParser.non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.anchor_parser.parseString(string)


# term_parser tests
class TestTermParser(object):
    matches = [
            ('$.a1.a2(1, 2, 3).a3|f1|f2|f3(a, "b, c", _d)|f4 tail',
                ('$', 
                    [
                        ('a1', ()),
                        ('a2', ('1', '2', '3')),
                        ('a3', ()),
                        ],
                    [
                        ('f1', ()),
                        ('f2', ()),
                        ('f3', ('a', 'b, c', '_d')),
                        ('f4', ()),
                        ],
                    ),
                ' tail'),
            ('  anchor . a (a,b,3)  |\tf tail',
                ('anchor',
                    [
                        ('a', ('a', 'b', '3')),
                        ],
                    [
                        ('f', ()),
                        ],
                    ),
                ' tail',),
            (' @ tail',
                ('@',
                    [],
                    [],
                    ),
                ' tail',),
            ('anchor .attr',
                ('anchor',
                    [
                        ('attr', ()),
                        ],
                    [],
                    ),
                '',),
            ('anchor|filter()',
                ('anchor',
                    [],
                    [
                        ('filter', ()),
                        ],
                    ),
                '()',),
            ]

    non_matches = [
            ('1id.a1.a2|f1|f2',),
            ('&.a1.a2|f1|f2',),
            ('.a1.a2|f1|f2',),
            ('|f1',),
            ]

    @staticmethod
    def check_term(term, anchor, accessors, filters):
        import screp.term_parser as module
        assert type(term) == module.ParsedTerm

        TestAnchorParser.check_anchor(term.anchor, anchor)

        assert len(term.accessors) == len(accessors)

        assert len(term.filters) == len(filters)

        for (a, match) in zip(term.accessors + term.filters, accessors + filters):
            TestActionParser.check_action(a, *match)


    @pytest.mark.parametrize(('string', 'match', 'tail'), matches)
    def test_matches(self, string, match, tail):
        import screp.term_parser as module
        module.term_parser.parseWithTabs()
        (ret, s, e) = module.term_parser.scanString(string, maxMatches=1).next()

        TestTermParser.check_term(ret[0], *match)

        assert string[e:].strip() == tail.strip()


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.term_parser as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.term_parser.parseString(string)



# csv_format_parser tests
class TestCSVFormatParser(object):
    matches = [
            ('$.a1(1, "a, bc", _id1), @.a2 | f1(1, _id2, ","), anchor',
                [
                    ( # anchor, accessors, filters
                        '$',
                        [
                            ('a1', ('1', 'a, bc', '_id1')),
                            ],
                        [],
                        ),
                    (
                        '@',
                        [
                            ('a2', ()),
                            ],
                        [
                            ('f1', ('1', '_id2', ',')),
                            ],
                        ),
                    (
                        'anchor',
                        [],
                        [],
                        ),
                    ],
                ),
            (
                'anchor1, anchor2,anchor3',
                [
                    (
                        'anchor1',
                        [],
                        [],
                        ),
                    (
                        'anchor2',
                        [],
                        [],
                        ),
                    (
                        'anchor3',
                        [],
                        [],
                        ),
                    ],
                ),
            (
                'anchor1.a1.a2(",") | f1 | f2(",") | f3',
                [
                    (
                        'anchor1',
                        [
                            ('a1', ()),
                            ('a2', (",",)),
                            ],
                        [
                            ('f1', ()),
                            ('f2', (',',)),
                            ('f3', ()),
                            ],
                        ),
                    ],
                ),
            ]



    non_matches = [
            ('1id.a1.a2 | f1 | f2',),
            ('id.a1 | f1, id.a2 | f2,',),
            ('',),
            (',',),
            ('id(1, "2").a1 | f1',),
            ]

    
    @pytest.mark.parametrize(('string', 'match'), matches)
    def test_matches(self, string, match):
        import screp.format_parsers as module

        ret = module.csv_format_parser.parseString(string)

        for (p, m) in zip(ret, match):
            TestTermParser.check_term(p, *m)


    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.format_parsers as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.csv_format_parser.parseString(string)


# json_format_parser tests
class TestJSONFormatParser(object):
    matches = [
            ('v1=$.a1.a2 | f1 | f2, v2=anchor.a3, v3=anchor | f3',
                [
                    # key, anchor, accessors, filters
                    (
                        'v1',
                        '$',
                        [
                            ('a1', ()),
                            ('a2', ()),
                            ],
                        [
                            ('f1', ()),
                            ('f2', ()),
                            ],
                        ),
                    (
                        'v2',
                        'anchor',
                        [
                            ('a3', ()),
                            ],
                        [],
                        ),
                    (
                        'v3',
                        'anchor',
                        [],
                        [
                            ('f3', ()),
                            ],
                        ),
                    ]),
            ('v1=$.a1(1, 2) | f1(1, "2 abc", 3), v_2=@, _v3=anchor | f1(1, 2)    ',
                [
                    (
                        'v1',
                        '$',
                        [
                            ('a1', ('1', '2')),
                            ],
                        [
                            ('f1', ('1', '2 abc', '3')),
                            ],
                        ),
                    (
                        'v_2',
                        '@',
                        [],
                        [],
                        ),
                    (
                        '_v3',
                        'anchor',
                        [],
                        [
                            ('f1', ('1', '2')),
                            ],
                        )
                    ]
                ),
                ]

    non_matches = [
            ('v1=',),
            ('',),
            ('v1=$,',),
            ('v2=1anchor.a1|f1',),
            ('v1=$.a1, v2=anchor, tail',),
            ('1v1=$.a1.a2 | f1 | f2',),
            ('v1=$.a1 | f1 . f2',),
            ]


    @staticmethod
    def check_pair_match(pair, match):
        assert pair[0] == match[0]
        TestTermParser.check_term(pair[1], *match[1:])


    @pytest.mark.parametrize(('string', 'match'), matches)
    def test_matches(self, string, match):
        import screp.format_parsers as module

        ret = module.json_format_parser.parseString(string)

        for (p, m) in zip(ret, match):
           TestJSONFormatParser.check_pair_match(p, m)

    
    @pytest.mark.parametrize(('string',), non_matches)
    def test_non_matches(self, string):
        import screp.format_parsers as module
        import pyparsing
        with pytest.raises(pyparsing.ParseException):
            ret = module.json_format_parser.parseString(string)


# general_format_parser tests
class TestGeneralFormatParser(object):
    matches = [
            ('{$.a1(1, 2).a2 | f1 | f2("123") } inter1 { anchor} tail',
                (['', ' inter1 ', ' tail'],
                    [
                        (# anchor, accessors, filters
                            '$',
                            [
                                ('a1', ('1', '2')),
                                ('a2', ()),
                                ],
                            [
                                ('f1', ()),
                                ('f2', ('123',)),
                                    ],
                            ),
                        (
                            'anchor',
                            [],
                            [],
                            ),
                        ],
                    ),
                ),
            ('123 no terms',
                (['123 no terms'],
                    [],
                    ),
                ),
            ('',
                ([''],
                    [],
                    ),
                ),
            ('$.a1 | f1} x y z {anchor. a2(1, 2) | f1 | f2} some tail',
                (['$.a1 | f1} x y z ', ' some tail'],
                    [
                        (
                            'anchor',
                            [
                                ('a2', ('1', '2')),
                                ],
                            [
                                ('f1', ()),
                                ('f2', ()),
                                ],
                            ),
                        ],
                    ),
                ),
            ('{anchor.a1} inter  1 {anchor.a2("}") | f2} {missing_curly.a1 | f1',
                (['', ' inter  1 ', ' {missing_curly.a1 | f1'],
                    [
                        ('anchor',
                            [
                                ('a1', ()),
                                ],
                            [],
                            ),
                        ('anchor',
                            [
                                ('a2', ('}',)),
                                ],
                            [
                                ('f2', ()),
                                ],
                            ),
                        ],
                    ),
                ),
            ('1\n2 {anchor1} 3 \t 4 {anchor2} \n\n\n',
                (['1\n2 ', ' 3 \t 4 ', ' \n\n\n'],
                    [
                        ('anchor1', [], []),
                        ('anchor2', [], []),
                        ],
                    ),
                ),
            ]

    non_matches = []

    @pytest.mark.parametrize(('string', 'match'), matches)
    def test_matches(self, string, match):
        import screp.format_parsers as format_parsers

        format_parsers.general_format_parser.parseWithTabs()

        ret = format_parsers.general_format_parser.parseString(string)

        (interstrings, terms) = match

        assert len(ret) % 2 == 1

        assert interstrings == ret[0::2]

        for (t, m) in zip(ret[1::2], terms):
            TestTermParser.check_term(t, *m)
