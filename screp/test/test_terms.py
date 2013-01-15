import pytest


class TestTermAction(object):

    @staticmethod
    def make_action(f, in_type=None, out_type=None):
        import screp.actions as module

        it = in_type
        ot = out_type

        class MockActionClass(module.BaseTermAction):
            in_type = it
            out_type = ot

            def execute(self, value):
                return f(value)

        return MockActionClass()


    def test_execute(self):
        value = 'value'
        
        def f(v):
            assert v == 'value'
            return 'result'


        action = TestTermAction.make_action(f)

        assert action.execute(value) == 'result'


    def test_execute_raises_exception(self):
        class BogusException(Exception):
            pass

        def f(v):
            raise BogusException()

        action = TestTermAction.make_action(f)

        with pytest.raises(BogusException):
            action.execute('value')


    can_follow_scenarios = [
            ('type1', 'type1'),
            (None, 'type1'),
            ('type1', None),
            (None, None),
            ]


    cannot_follow_scenarios = [
            ('type1', 'type2'),
            ]


    @pytest.mark.parametrize(('t1', 't2'), can_follow_scenarios)
    def test_can_follow(self, t1, t2):
        action1 = TestTermAction.make_action(lambda x: x, out_type=t1)
        action2 = TestTermAction.make_action(lambda x: x, in_type=t2)

        assert action2.can_follow(action1)


    @pytest.mark.parametrize(('t1', 't2'), cannot_follow_scenarios)
    def test_cannot_follow(self, t1, t2):
        action1 = TestTermAction.make_action(lambda x: x, out_type=t1)
        action2 = TestTermAction.make_action(lambda x: x, in_type=t2)

        assert not action2.can_follow(action1)


    @pytest.mark.parametrize(('t1', 't2'), can_follow_scenarios)
    def test_can_precede(self, t1, t2):
        action1 = TestTermAction.make_action(lambda x: x, out_type=t1)
        action2 = TestTermAction.make_action(lambda x: x, in_type=t2)

        assert action1.can_precede(action2)


    @pytest.mark.parametrize(('t1', 't2'), cannot_follow_scenarios)
    def test_cannot_precede(self, t1, t2):
        action1 = TestTermAction.make_action(lambda x: x, out_type=t1)
        action2 = TestTermAction.make_action(lambda x: x, in_type=t2)

        assert not action1.can_precede(action2)


class TestTerm(object):
    @staticmethod
    def make_term(actions):
        import screp.actions as module
        return module.Term(actions)


    def test_execute(self):
        def f(in_value):
            assert in_value == 'in_value'
            return 'out_value'

        term = TestTerm.make_term([TestTermAction.make_action(f)],)

        assert term.execute('in_value') == 'out_value'


    def test_execute_value_passing(self):
        def f1(in_value):
            assert in_value == 'value1'
            return 'value2'

        def f2(in_value):
            assert in_value == 'value2'
            return in_value + 'value3'

        term = TestTerm.make_term([TestTermAction.make_action(f1),
            TestTermAction.make_action(f2)])

        assert term.execute('value1') == 'value2value3'


    def test_execute_raises_exception(self):
        class BogusException(Exception):
            pass

        def f(v):
            raise BogusException()

        term = TestTerm.make_term([TestTermAction.make_action(f)])

        with pytest.raises(BogusException):
            term.execute('value')


    def test_initialization(self):
        # TODO:
        pass


    def test_execute_no_actions_defined(self):
        term = TestTerm.make_term([])

        with pytest.raises(Exception):
            term.execute('value')


    def test_add_action(self):
        def f1(v):
            return v + '1'

        def f2(v):
            return v + '2'

        term = TestTerm.make_term([])

        term.add_action(TestTermAction.make_action(f1, out_type='t1'))

        assert term.execute('0') == '01'

        term.add_action(TestTermAction.make_action(f2, in_type='t1'))

        assert term.execute('0') == '012'


    def test_add_action_cannot_follow(self):
        term = TestTerm.make_term([TestTermAction.make_action(lambda x: x, out_type='t1')])

        with pytest.raises(TypeError):
            term.add_action(TestTermAction.make_action(lambda x: x, in_type='t2'))

    
    def test_last_action(self):
        term = TestTerm.make_term([TestTermAction.make_action(lambda x: x, out_type='t1')])

        la = TestTermAction.make_action(lambda x: x, in_type='t1', out_type='t2')
        term.add_action(la)

        assert term.last_action == la


    def test_out_type(self):
        term = TestTerm.make_term([TestTermAction.make_action(lambda x: x, out_type='t1')])

        assert term.out_type == 't1'


    def test_out_type_none(self):
        term = TestTerm.make_term([])

        assert term.out_type is None


class TestGenericTermAction(object):

    def test_creation(self):
        pass

    
    def test_execute(self):
        pass


    def test_initialization(self):
        pass


    def test_execute_raises_exception(self):
        pass


class TestSelectorTermAction(object):

    def test_initialization(self):
        pass


    def test_erroneous_selector(self):
        pass


class TestAnchorTermAction(object):
    class BogusContext(object):
        def __init__(self, get_anchor):
            self._get_anchor = get_anchor

        
        def get_anchor(self, key):
            return self._get_anchor(key)


    @staticmethod
    def make_context(f):
        return TestAnchorTermAction.BogusContext(f)


    @staticmethod
    def make_anchor_term_action(key):
        import screp.actions as module
        return module.AnchorTermAction(key)


    def test_get_anchor(self):
        def f(k):
            assert k == 'anchor'
            return 'value'

        context = TestAnchorTermAction.make_context(f)

        a = TestAnchorTermAction.make_anchor_term_action('anchor')

        assert a.execute(context) == 'value'


    def test_get_anchor_raises(self):
        class BogusException(Exception):
            pass

        def f(k):
            raise BogusException()

        context = TestAnchorTermAction.make_context(f)

        a = TestAnchorTermAction.make_anchor_term_action('anchor')

        with pytest.raises(BogusException):
            a.execute(context)


class Test_make_action(object):

    def setup_actions_dir(self, monkeypatch, mock_actions):
        import screp.actions as module

        monkeypatch.setattr(module, 'actions_dir', dict(module.multiply_keys(mock_actions)))


    def test_make_action(self, monkeypatch):
        import screp.actions as module
        from screp.term_parser import ParsedTermAction

        mock_ids = ('action', 'a')
        mock_args = [1, 2, 'three']
        mock_value = 'value'

        def action_builder(identification, args):
            assert identification in mock_ids
            assert args is mock_args

            return mock_value

        self.setup_actions_dir(monkeypatch, [
            (mock_ids,   action_builder),
            ])

        a1 = module.make_action(ParsedTermAction('action', 1, mock_args))

        a2 = module.make_action(ParsedTermAction('a', 1, mock_args))

        assert a1 == mock_value and a2 == mock_value


    def test_make_action_not_found(self, monkeypatch):
        import screp.actions as module
        from screp.term_parser import ParsedTermAction

        self.setup_actions_dir(monkeypatch, [
            (('action',),   lambda id, args: 'value'),
            ])

        with pytest.raises(KeyError):
            module.make_action(ParsedTermAction('other_action', 1, []))


class Test_make_term(object):
    # TODO
    pass


class Test_make_anchor(object):
    # TODO
    pass
