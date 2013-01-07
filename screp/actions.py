import types
import lxml
import lxml.etree
from lxml.cssselect import CSSSelector

from .context import XMLContext


supported_types = ['element', 'element_set', 'string', 'context']


def types_match(t1, t2):
    return (t1 is None) or (t2 is None) or (t1 == t2)


class BasePipeUnit(object):
    in_type = None
    out_type = None


    def can_follow(self, other):
        return types_match(other.out_type, self.in_type)


    def can_precede(self, other):
        return types_match(self.out_type, other.in_type)


    def execute(self, value, *extras):
        pass


class GenericPipeUnit(BasePipeUnit):
    def __init__(self, f, in_type=None, out_type=None, name=None, extras=None):
        self.name = name
        self.f = f
        self.in_type = in_type
        self.out_type = out_type
        if extras is None:
            extras = []
        self.extras = extras


    def execute(self, value):
        return self.f(value, *self.extras)


    def __str__(self):
        return "PipeAction<%s(%s) => %s>" % (self.name, self.in_type, self.out_type)


class SelectorPipeUnit(GenericPipeUnit):
    def __init__(self, f, in_type=None, out_type=None, name=None, extras=None):
        super(SelectorPipeUnit, self).__init__(f, in_type=in_type, out_type=out_type, name=name, extras=extras)

        self.selector = CSSSelector(self.extras[0])
        del self.extras[0]


    def execute(self, value):
        return self.f(value, self.selector, *self.extras)


class Pipe(object):
    def __init__(self, initial_action=None):
        self._actions = []
        if initial_action is not None:
            self._actions.append(initial_action)


    def append_action(self, action):
        if len(self._actions) == 0:
            self._actions.append(action)
        else:
            last = self._actions[-1]
            if not last.can_precede(action):
                raise TypeError("Action %s cannot follow action %s (especting type '%s', got '%s')" %\
                        (action, last, action.in_type, last.out_type))
            self._actions.append(action)


    def execute(self, value):
        for a in self._actions:
            value = a.execute(value)

        return value


def make_unit_of_class(cls, f, in_type, out_type):
    def builder(name, extras):
        return cls(f, in_type=in_type, out_type=out_type, name=name, extras=extras)

    return builder


def make_generic_unit(f, in_type, out_type):
    return make_unit_of_class(GenericPipeUnit, f, in_type, out_type)


def make_selector_unit(f, in_type, out_type):
    return make_unit_of_class(SelectorPipeUnit, f, in_type, out_type)


actions = [
        # accessors
        (('first', 'f'),    make_generic_unit(lambda s: s[0], 'element_set', 'element')),
        (('last', 'l'),     make_generic_unit(lambda s: s[-1], 'element_set', 'element')),
        (('class', 'c'),    make_generic_unit(lambda e: e.get('class'), 'element', 'string')),
        (('parent', 'p'),   make_generic_unit(lambda e: e.getparent(), 'element', 'element')),
        (('text', 't'),     make_generic_unit(lambda e: e.text, 'element', 'string')),
        (('tag',),          make_generic_unit(lambda e: e.tag, 'element', 'string')),
        (('attr', 'a'),     make_generic_unit(lambda e, a: e.get(a), 'element', 'string')),
        (('nth', 'n'),      make_generic_unit(lambda s, i: s[i], 'element_set', 'element')),
        (('desc', 'd'),     make_selector_unit(lambda e, sel: sel(e), 'element', 'element_set')),
        (('first-desc', 'fd'),  make_selector_unit(lambda e, sel: sel(e)[0], 'element', 'element')),

        # functions/filters
        (('upper',),        make_generic_unit(lambda s: s.upper(), 'string', 'string')),
        (('lower',),        make_generic_unit(lambda s: s.lower(), 'string', 'string')),
        (('trim',),         make_generic_unit(lambda s: s.strip(), 'string', 'string')),

        # anchors
        (('$',),            make_generic_unit(lambda c: c.current, 'context', 'element')),
        (('@',),            make_generic_unit(lambda c: c.root, 'context', 'element')),
        ]


def multiply_keys(lst):
    for keys, val in lst:
        for k in keys:
            yield (k, val)


actions_dir = dict(multiply_keys(actions))


def make_action(action_name, extras=None):
    if extras is None:
        extras = []
    return actions_dir[action_name](action_name, extras)


def make_pipe(actions):
    pipe = Pipe()

    for a in actions:
        pipe.append_action(a)

    return pipe
