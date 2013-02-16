import pytest


class TestAnchorContext(object):
    def make_context(self, primary_anchors):
        import screp.context as context

        return context.AnchorContext(primary_anchors)


    def test_get_anchor(self):
        context = self.make_context({'a1': 1, 'a2': 2})

        assert context.get_anchor('a1') == 1

        assert context.get_anchor('a2') == 2


    def test_get_anchor_not_found(self):
        context = self.make_context({'a1': 1, 'a2': 2})

        with pytest.raises(Exception):
            context.get_anchor('a3')


    def test_add_anchor(self):
        context = self.make_context({'a1': 1, 'a2': 2})

        context.add_anchor('a3', 3)

        assert context.get_anchor('a3') == 3

        assert context.get_anchor('a1') == 1

        context.add_anchor('a1', 4)

        assert context.get_anchor('a1') == 4


class TestAnchorContextFactory(object):
    def make_factory(self, primary_anchors):
        import screp.context as context

        return context.AnchorContextFactory(primary_anchors)


    def make_identity_anchor(self, name, out_type):
        import screp.anchor as anchor_module
        import screp.term as term_module
        import screp.termactions as termactions_module

        return anchor_module.Anchor(name, term_module.Term([termactions_module.AnchorTermAction(name, out_type)]))


    def test_get_anchor(self):
        factory = self.make_factory([('a1', 't1'), ('a2', 't2')])

        a1 = factory.get_anchor('a1')
        a2 = factory.get_anchor('a2')

        assert a1.name == 'a1' and a1.out_type == 't1'
        assert a2.name == 'a2' and a2.out_type == 't2'


    def test_get_anchor_not_found(self):
        factory = self.make_factory([('a1', 't1'), ('a2', 't2')])

        with pytest.raises(Exception):
            factory.get_anchor('a3')


    def test_add_anchor(self):
        factory = self.make_factory([('a1', 't1')])

        a1 = factory.get_anchor('a1')

        assert a1.name == 'a1' and a1.out_type == 't1'

        factory.add_anchor(self.make_identity_anchor('a1', 't2'))

        a1 = factory.get_anchor('a1')

        assert a1.name == 'a1' and a1.out_type == 't2'

        factory.add_anchor(self.make_identity_anchor('a1', 't3'))

        a1 = factory.get_anchor('a1')

        assert a1.name == 'a1' and a1.out_type == 't3'


    def test_make_context(self):
        from screp.anchor import Anchor
        from screp.term import Term
        from screp.termactions import (
                AnchorTermAction,
                GenericTermAction,
                )

        factory = self.make_factory([('a1', 't1')])

        factory.add_anchor(Anchor('a2', Term([
            AnchorTermAction('a1', 't1'),
            GenericTermAction(lambda x: x + 'b', in_type='t1', out_type='t2'),
            ])))

        factory.add_anchor(Anchor('a1', Term([
            AnchorTermAction('a1', 't1'),
            GenericTermAction(lambda x: x + 'c', in_type='t1', out_type='t3'),
            GenericTermAction(lambda x: x + 'd', in_type='t3', out_type='t4'),
            ])))

        factory.add_anchor(Anchor('a3', Term([
            AnchorTermAction('a1', 't4'),
            GenericTermAction(lambda x: x + 'e', in_type='t4', out_type='t5'),
            ])))

        context = factory.make_context({'a1': 'a'})

        assert context.get_anchor('a1') == 'acd'

        assert context.get_anchor('a2') == 'ab'

        assert context.get_anchor('a3') == 'acde'


    def test_make_context_primary_anchor_missing(self):
        from screp.anchor import Anchor
        from screp.term import Term
        from screp.termactions import (
                AnchorTermAction,
                GenericTermAction,
                )

        factory = self.make_factory([('a1', 't1')])

        factory.add_anchor(Anchor('a2', Term([
            AnchorTermAction('a1', 't1'),
            GenericTermAction(lambda x: x + 'b', in_type='t1', out_type='t2'),
            ])))

        with pytest.raises(Exception):
            context = factory.make_factory({'a3': 'xxx'})


    def test_make_identity_anchor_action(self):
        from screp.anchor import Anchor
        from screp.term import Term
        from screp.termactions import (
                AnchorTermAction,
                GenericTermAction,
                )
        from screp.context import (
                AnchorContext,
                )

        factory = self.make_factory([('a1', 't1')])

        factory.add_anchor(Anchor('a2', Term([
            AnchorTermAction('a1', 't1'),
            GenericTermAction(lambda x: x + 'b', in_type='t1', out_type='t2'),
            ])))

        action1 = factory.make_anchor_action('a1', 'identification')

        action2 = factory.make_anchor_action('a2', 'identification')

        assert action1.out_type == 't1' and action1.execute(AnchorContext({'a1': 'x'})) == 'x'

        assert action2.out_type == 't2' and action2.execute(AnchorContext({'a2': 'y'})) == 'y'
