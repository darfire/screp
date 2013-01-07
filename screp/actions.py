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


def make_unit_of_class(cls, f, in_type, out_type):
    def f(name, extras):
        return cls(f, in_type=in_type, out_type=out_type, name=name, extras=extras)

    return f


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
        (('upper',)         make_generic_unit(lambda s: s.upper(), 'string', 'string')),
        (('lower',)         make_generic_unit(lambda s: s.lower(), 'string', 'string')),
        (('trim',)         make_generic_unit(lambda s: s.strip(), 'string', 'string')),
        ]



class TermAction(object):
    def __init__(self, f, validator=None, f_args=None, name=None):
        self._f = f
        self._validator = validator

        if f_args is None:
            f_args = []

        self._f_args = f_args

        self.name = name


    def execute(self, val):
        if self._validator is not None:
            self._validator(val)

        return self._f(val, *self._f_args)


    def __str__(self):
        return "TermAction(%s, %s)" % (self.name, self._f_args)


    __repr__ = __str__


class TermActionSet(object):
    def __init__(self, actions):
        self._actions = actions


    def append_action(self, action):
        self._actions.append(action)


    def execute(self, obj):
        for a in self._actions:
            obj = a.execute(obj)

        return obj


    @staticmethod
    def from_term(anchor, accessors, functions):
        return TermActionSet([anchor] + accessors + functions)


    def __str__(self):
        return "TermActionSet(%s)" % (', '.join(map(lambda ta: ta.name, self._actions)),)


    __repr__ = __str__


# validators

def check_type(o, t):
    if type(o) != t:
        raise TypeError('Expecting object of type %s, got %s' % (t, type(o)))

def elset_validator(s):
    check_type(s, types.ListType)
    if len(s) > 0:
        ts = set(map(type, s))
        if len(ts) > 1 or element_type not in ts:
            raise TypeError('Expecting a list of Elements. Got %s' % (ts,))


def element_validator(e):
    check_type(e, element_type)


def context_validator(c):
    check_type(c, XMLContext)


def string_validator(s):
    check_type(s, types.StringType)


# accessors

def children_accessor_f(el, css):
    return []


def desc_accessor_f(el, css):

    sel = CSSSelector(css)
    r = sel(el)

    return r



actions = {
        # accessors
        'first': (lambda s: s[0], elset_validator),  # elset => element
        'last': (lambda s: s[-1], elset_validator),    # elset => element
        'class': (lambda e: e.get('class'), element_validator),    # element => string
        'parent': (lambda e: e.getparent(), element_validator),  # element => element
        'text': (lambda e: e.text, element_validator),  # element => string
        'tag': (lambda e: e.tag, element_validator),    # element => string
        'children': (children_accessor_f, element_validator), # element => elset
        'desc': (desc_accessor_f, element_validator), # element => elset
        'nth': (lambda elset, idx: elset[idx], elset_validator), # elset => element
        'attr': (lambda el, attr: el.get(attr), element_validator), # element => string

        # functions
        'upper': (lambda s: s.upper(), string_validator),   # string => string
        'lower': (lambda s: s.lower(), string_validator),   # string => string
        'trim': (lambda s: s.strip(), string_validator),     # string => string

        # anchors
        '$':    (lambda c: c.current, context_validator),   # context => element
        '@':    (lambda c: c.root, context_validator),      # context => element
        }


def make_action(action_name, extra_args=None):
    (f, v) = actions[action_name]
    return TermAction(f, validator=v, f_args=extra_args, name=action_name)

