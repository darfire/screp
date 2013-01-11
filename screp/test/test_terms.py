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


    def test_execute_throws_exception(self):
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


    def test_name(self):
        # TODO:
        pass


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


    def test_execute_throws_exception(self):
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
        # TODO:
        pass
