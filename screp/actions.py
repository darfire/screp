import types
import lxml
from lxml.etree import XPath
from lxml.cssselect import (
        CSSSelector,
        css_to_xpath,
        )

from .context import XMLContext


supported_types = ['element', 'element_set', 'string', 'context']


class BaseTermAction(object):
    in_type = None
    out_type = None

    @staticmethod
    def _check_types_match(t1, t2):
        return (t1 is None) or (t2 is None) or (t1 == t2)


    def can_precede(self, other):
        return BaseTermAction._check_types_match(self.out_type, other.in_type)


    def can_follow(self, other):
        return BaseTermAction._check_types_match(self.in_type, other.out_type)


    def execute(self, value):
        pass


class GenericTermAction(BaseTermAction):
    def __init__(self, f, in_type=None, out_type=None, args=None, identification=None):
        self._f = f
        self._id = identification
        self.in_type = in_type
        self.out_type = out_type
        if args is None:
            args = []
        self._args = list(args)


    def execute(self, value):
        return self._f(value, *self._args)


class SelectorTermAction(GenericTermAction):
    def __init__(self, f, in_type=None, out_type=None, identification=None, args=None):
        super(SelectorTermAction, self).__init__(f, in_type=in_type, out_type=out_type, identification=identification, args=args)

        self._selector = CSSSelector(self._args[0])

        del self._args[0]


    def execute(self, value):
        return self._f(value, self._selector, *self._args)


class AxisSelectorTermAction(GenericTermAction):
    def __init__(self, f, axis, in_type=None, out_type=None, identification=None, args=None):
        super(AxisSelectorTermAction, self).__init__(f, in_type=in_type, out_type=out_type, identification=identification, args=args)

        self._selector = XPath(css_to_xpath(self._args[0], prefix=axis))

        del self._args[0]


    def execute(self, value):
        return self._f(value, self._selector, *self._args)


class CustomSelectorTermAction(GenericTermAction):
    in_type = 'element'
    out_type = 'element_set'

    def __init__(self, f, selector_class, in_type=None, out_type=None, identification=None, args=None):
        super(CustomSelectorTermAction, self).__init__(f, in_type=in_type, out_type=out_type, identification=identification, args=args)

        self._selector = selector_class(self._args[0])

        del self._args[0]


    def execute(self, value):
        return self._f(value, self._selector, *self._args)


class SiblingSelector(object):
    def __init__(self, selector):
        self._preceding_sel = XPath(css_to_xpath(selector, prefix="preceding-sibling::"))
        self._following_sel = XPath(css_to_xpath(selector, prefix="following-sibling::"))


    def __call__(self, element):
        return self._preceding_sel(element) + self._following_sel(element)


class AnchorTermAction(BaseTermAction):
    in_type = 'context'
    out_type = 'element'

    def __init__(self, anchor):
        self._anchor = anchor


    def execute(self, value):
        # value must be a context
        return value.get_anchor(self._anchor)


class Term(object):
    def __init__(self, actions=None):
        if actions is None:
            actions = []

        self._actions = []

        for a in actions:
            self.add_action(a)


    def add_action(self, action):
        if len(self._actions) > 0:
            if not action.can_follow(self.last_action):
                raise TypeError('%s cannot follow %s: expects type %s, receives %s'\
                        % (action, self.last_action, action.in_type, self.last_action.out_type))
        self._actions.append(action)


    @property
    def last_action(self):
        return self._actions[-1]


    def execute(self, value):
        if len(self._actions) == 0:
            raise ValueError("No actions defined")

        for a in self._actions:
            value = a.execute(value)

        return value


    @property
    def out_type(self):
        if len(self._actions) == 0:
            return None
        else:
            return self.last_action.out_type


class Anchor(object):
    def __init__(self, name, term):
        self.name = name
        self.term = term


    def execute(self, context):
        return self.term.execute(context)


def make_action_of_class(cls, f, in_type, out_type):
    def builder(identification, args):
        return cls(f, in_type=in_type, out_type=out_type, identification=identification, args=args)

    return builder


def make_generic_action(f, in_type, out_type):
    return make_action_of_class(GenericTermAction, f, in_type, out_type)


def make_selector_action(f, in_type, out_type):
    return make_action_of_class(SelectorTermAction, f, in_type, out_type)


def make_x_selector_action(f, axis, in_type, out_type):
    def builder(identification, args):
        return AxisSelectorTermAction(f, axis, in_type=in_type, out_type=out_type, identification=identification, args=args)

    return builder


def make_custom_selector_action(f, selector_class, in_type, out_type):
    def builder(identification, args):
        return CustomSelectorTermAction(f, selector_class, in_type=in_type, out_type=out_type, identification=identification, args=args)

    return builder


def match_selector(elset, selector):
    return sum(map(selector, elset), [])


def get_attr(element, attr):
    v = element.get(attr)
    if v is None:
        raise KeyError("Element doesn't have attribute '%s'" % (attr,))
    else:
        return v


def get_parent(element):
    parent = element.getparent()

    if parent is None:
        raise ValueError("Could not get parent: element is root")
    else:
        return parent


actions = [
        # accessors
        (('first', 'f'),            make_generic_action(lambda s: s[0], 'element_set', 'element')),
        (('last', 'l'),             make_generic_action(lambda s: s[-1], 'element_set', 'element')),
        (('class',),                make_generic_action(lambda e: get_attr(e, 'class'), 'element', 'string')),
        (('id',),                   make_generic_action(lambda e: get_attr(e, 'id'), 'element', 'string')),
        (('parent', 'p'),           make_generic_action(lambda e: get_parent(e), 'element', 'element')),
        (('text',),                 make_generic_action(lambda e: e.text, 'element', 'string')),
        (('tag',),                  make_generic_action(lambda e: e.tag, 'element', 'string')),
        (('attr', 'a'),             make_generic_action(lambda e, a: get_attr(e, a), 'element', 'string')),
        (('nth', 'n'),              make_generic_action(lambda s, i: s[i], 'element_set', 'element')),
        (('desc', 'd'),             make_selector_action(lambda e, sel: sel(e), 'element', 'element_set')),
        (('first-desc', 'fd'),      make_selector_action(lambda e, sel: sel(e)[0], 'element', 'element')),
        (('ancestors', 'ancs'),     make_x_selector_action(lambda e, sel: sel(e), 'ancestor::', 'element', 'element_set')),
        (('children', 'kids'),      make_x_selector_action(lambda e, sel: sel(e), 'child::', 'element', 'element_set')),
        (('fsiblings', 'fsibs'),    make_x_selector_action(lambda e, sel: sel(e), 'following-sibling::', 'element', 'element_set')),
        (('psiblings', 'psibs'),    make_x_selector_action(lambda e, sel: sel(e), 'preceding-sibling::', 'element', 'element_set')),
        (('siblings', 'sibs'),      make_custom_selector_action(lambda e, sel: sel(e), SiblingSelector, 'element', 'element_set')),
        (('matching', 'm'),         make_x_selector_action(match_selector, 'self::', 'element_set', 'element_set')),


        # functions/filters
        (('upper',),                make_generic_action(lambda s: s.upper(), 'string', 'string')),
        (('lower',),                make_generic_action(lambda s: s.lower(), 'string', 'string')),
        (('trim', 't'),             make_generic_action(lambda s: s.strip(), 'string', 'string')),
        (('strip',),                make_generic_action(lambda s, chars: s.strip(chars), 'string', 'string')),
        (('replace',),              make_generic_action(lambda s, old, new: s.replace(old, new), 'string', 'string')),
        ]


def multiply_keys(lst):
    for keys, val in lst:
        for k in keys:
            yield (k, val)


actions_dir = dict(multiply_keys(actions))


def make_action(parsed_action):
    try:
        return actions_dir[parsed_action.name](parsed_action.name, parsed_action.args)
    except KeyError:
        raise KeyError('Unknown action %s' % (parsed_action.location,))


def make_term(pterm, required_out_type=None):
    actions = [AnchorTermAction(pterm.anchor.name)] + map(lambda ta: make_action(ta), pterm.accessors + pterm.filters)
    if required_out_type is not None:
        if len(actions) == 0 or actions[-1].out_type != required_out_type:
            raise ValueError("Term must have out_type '%s', has '%s'!" % (required_out_type, actions[-1].out_type))
    return Term(actions)


def make_anchor(name, pterm):
    term = make_term(pterm, required_out_type='element')

    return Anchor(name, term)
