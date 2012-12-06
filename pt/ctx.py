"""
Runtime functionaly (uses template context).
"""

from cgi import escape as xml_escape

class Undefined(object):
    """Undefined object."""
    def __nonzero__(self):
        return False
    def __unicode__(self):
        raise Exception("UNDEFINED")

UNDEFINED = Undefined()
Undefined = None

def Var(name, default=UNDEFINED, format=None, escape="xml"): # attr=None,True,False
    """Generate function-resolver of given variable in context. Optionally format and escape resolved value.
    @default - default value, if no default value is provided and var isn't resolved will be raised KeyError.
    @f - mask like "%.2f" or formatter function, that receives value as first argument.
    @e - escaping mode, one from ["xml", "js", "--", 0], default is "xml".
    """
    tokens = name.split('.')
    if len(tokens) == 1:
        def ctx_getter(ctx):
            value = ctx.get(name, default)
            if value is UNDEFINED:
                raise Exception("Can't resolve variable %r, available keys=%r" % (name, ctx.keys()))
            return value
    else:
        def check_undefined(value, token):
            if value is UNDEFINED and default is UNDEFINED:
                raise Exception("Can't resolve variable %r, failed at %s." % (name, token))
            return value is UNDEFINED

        head, tail = tokens[0], tokens[1:]
        def ctx_getter(ctx):
            value = ctx.get(head, UNDEFINED)
            if check_undefined(value, head):
                return default
            for token in tail:
                attr = getattr(value, token, UNDEFINED)
                if attr is not UNDEFINED:
                    value = attr
                elif value:
                    value = value.get(token, UNDEFINED)
                else:
                    value = UNDEFINED
                if check_undefined(value, token):
                    return default
            return value
    if format:
        if isinstance(format, basestring):
            # convert formatter string to function
            pattern = unicode(format)
            format = lambda value: pattern % value
    if escape == "xml":
        escape = xml_escape
    elif escape:
        raise Exception("Unknown escape mode: %r" % escape)
    if not format and not escape:
        return ctx_getter               # return value without formatting and escaping
    def get_format_escape(ctx):
        value = ctx_getter(ctx)
        if format:
            value = format(value)
        if escape:
            value = escape(value)
        return value
    return get_format_escape


def SafeVar(name, default=UNDEFINED, format=None):
    """Shortcut to Var without esaping.
    Usefull for non-html templates where escaping isn't need, for outputing safe values like digits or
    checked html markup.
    """
    return Var(name, default, format, False)

def resolve(ctx, token):
    """Resolve token (var or plain object) in current context and return it's value.
    """
    return token(ctx) if callable(token) else token

def resolve_args(ctx, args):
    return args and [resolve(ctx, token) for token in args]

def resolve_kwargs(ctx, kwargs):
    return kwargs and dict((k, resolve(ctx, v)) for k, v in kwargs.iteritems())

def Function(func, *args, **kwargs):
    """Return invoker of a function with given kwargs and ctx.
    """
    def func_invoker(ctx):
        return func(*resolve_args(ctx, args), **resolve_kwargs(ctx, kwargs))
    return func_invoker

def CtxRef(ctx):
    """Context reference for passign context into user function.
    >>> from pt.demo.env import E
    >>> def greeting(ctx, name): return u"Hello, %s from %s!" % (E(name), ctx['REMOTE_IP'])
    >>> Function(greeting, CtxRef, "Guest")({'REMOTE_IP': '127.0.0.1'})
    u'Hello, Guest from 127.0.0.1!'
    """
    return ctx

class Enum(object):
    """A sequence wrapper with access to first(index), last(index) and length properties.
    If sequence doesn't have __len__, convert it to list.
    >>> enum = Enum(range(3))
    >>> [(item, enum.first(i), enum.last(i)) for i, item in enum]
    [(0, True, False), (1, False, False), (2, False, True)]
    """

    def __init__(self, seq):
        self.seq = hasattr(seq, '__len__') and seq or list(seq)
        self._length = len(self.seq)
        return super(Enum, self).__init__()

    def first(self, index):
        return index == 0

    def last(self, index):
        return index == self._length - 1

    def __iter__(self):
        return enumerate(self.seq)

    def __len__(self):
        return self._length

def Maybe(*args):
    """Takes pairs (value, predicate), evaluates predicates and return value for matched predicate.
    If all predicates returned False, return None. If predicate is callable (can't be evaluated at
    compile time), then return function that will evaluate such predicate and all next predicates
    at runtime.
    >>> Maybe("No", False, "Yes", True)
    'Yes'
    >>> enum = Enum(range(3))
    >>> [(item, Maybe("first", i==0, "last", enum.last(i))) for i, item in enum]
    [(0, 'first'), (1, None), (2, 'last')]
    >>> from pt.demo.env import div, Template, Maybe, S
    >>> doc = Template() [div(cls=Maybe("active", S("user", None)))]
    >>> doc.render({'user': 'tester'})
    u'<div class="active"></div>'
    >>> doc.render({})                  # no class attribute at all
    u'<div></div>'
    """
    assert len(args) % 2 == 0, "Pairs (value, predicate) are expected."
    _runtime = []
    for value, predicate in zip(args[::2], args[1:][::2]):
        if _runtime or callable(predicate):
            _runtime.append((value, predicate))
        elif predicate: # no runtime predicates so far
            return value
    if _runtime:
        return lambda ctx: _runtime_maybe(ctx, _runtime)

def _runtime_maybe(ctx, variants):
    """Check predicates at runtime and return matched value or None."""
    for value, predicate in variants:
        if callable(predicate):
            if predicate(ctx):
                return value
        elif predicate:
            return value
