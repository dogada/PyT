"""
Document Object Model of templates.
"""

from itertools import chain
from pt.utils import coroutine, append_sent, join_sent, join_strings

PREPROCESS_FLAG = '_pt_preprocess'      # function with this attribute will be preprocessed
DEFAULT_VISITORS = {}                   # default type->visitor_func map

class Node(object):

    def __init__(self, name='', attrs={}, content=[]):
        self.name = name
        self.attrs = attrs
        self.content = content

    def __call__(self, **attrs):
        """Return new node subclass with new attrs and same content.
        For 'class' attribute use 'cls' name, for example div(cls="main") or pass it as
        div(**{'class': "main"}). If 'cls' and 'class' used together error is raised.
        """
        if 'cls' in attrs:
            assert 'class' not in attrs, "'cls' and 'class' attribute names used together."
            attrs['class'] = attrs.pop('cls')
        return self.__class__(self.name, attrs, self.content)

    def __len__(self):
        return len(self.content)

    def _check_content(self, content):
        if not hasattr(content, '__iter__'):
            content = [content]
        return  content

    def __getitem__(self, content):
        assert content is not None
        #if not isinstance(content, (tuple, list)):
        return self.__class__(self.name, self.attrs, self._check_content(content))

    def __unicode__(self):
        return unicode(self.name)

    def __repr__(self):
        return "<%s: %s, attrs=%s, content=%d>" % \
               (self.__class__.__name__, self.name, len(self.attrs), len(self.content))

class Element(Node):
    """(X)HTML element with content."""

class EmptyElement(Element):
    """Possibly empty (x)html element, like <meta />, <br />, <p />."""

    def __getitem__(self, content):
        assert content == "", "Empty elements can't have other content but empty string."
        return Element.__getitem__(self, content)

class Comment(Element):
    """Comment node with comment escaping when only '--' is escaped."""

class PI(Node):
    """Processing instruction."""

class Block(Node):
    """Document fragment that holds list of nodes.
    """
    def __init__(self, name='', attrs={}, content=[], **kwargs):
        super(Block, self).__init__(name, attrs, content)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __call__(self, *args, **kwargs):
        raise Exception("Invalid usage. Parameters are accepted in __init__ only: %s" % self)

    def __getitem__(self, content):
        copy = self.__class__(**self.__dict__)
        copy.content = self._check_content(content)
        return copy

    def __iter__(self):
        for obj in self.content:
            yield obj

def preprocess(func):
    """Add to function preprocess flag that Template takes into account if preprocessing is enabled.
    """
    assert callable(func)
    setattr(func, PREPROCESS_FLAG, True)
    return func


def execute_callable(walker, obj):
    walker(obj(walker.ctx))

def preprocess_callable(walker, obj):
    if hasattr(obj, PREPROCESS_FLAG):
        res = obj(None)
        if res is not None:
            walker.emit_gen.send(res)
    else:
        walker.emit_gen.send(obj)

def read_callable(walker, obj):
    walker.emit_gen.send(obj)

def make_walker(callable_visitor, visitors, emit_gen, ctx, indent_step=u''):
    """Faster version of classical walker.
    Powered by closure of important params and emit generator.
    >>> fast_walk = make_walker(execute_callable, {}, None, {})
    >>> fast_walk.__name__, fast_walk.emit_gen, fast_walk.ctx
    ('default_walker', None, {})
    >>> debug_walk = make_walker(execute_callable, {}, None, {}, indent_step=u'  ')
    >>> debug_walk.__name__, debug_walk.emit_gen, debug_walk.ctx, debug_walk.indent
    ('indent_walker', None, {}, 0)
    """
    walker = None                       # will hold reference to actual worker
    def default_walker(obj):            # no spaces between xml elements
        try:
            visitor = visitors[type(obj)]
        except:                         # KeyError
            if hasattr(obj, '__iter__'):
                # iterate Block, Template and subclasess, tuple, list, generator, etc
                for i in obj:
                    walker(i)
            elif callable(obj):
                callable_visitor(walker, obj)
            elif obj is not None:                               # int, string, etc convert to unicode
                emit_gen.send(unicode(obj))
        else:
            visitor(walker, obj)

    def indent_walker(obj):             # indent xml elements
        if isinstance(obj, Node) and not isinstance(obj, Block):
            if indent_walker.indent:
                emit_gen.send(u'\n')
                emit_gen.send(indent_step*indent_walker.indent)
        default_walker(obj)
    indent_walker.indent = 0

    walker = indent_walker if indent_step else default_walker 
    walker.emit_gen = emit_gen
    walker.ctx = ctx
    walker.blocks = []                  # parent blocks stack for Super resolving
    return walker

class _Super(Node):
    """Reference a super block inside a block."""
    pass

Super = _Super()                        # singletone for use in templates

class Template(Block):
    visitors = DEFAULT_VISITORS
    normalize = True
    preprocess = True
    indent_step = u''
    _default_cache_key = ""

    def extend(self, blocks=[], **kwargs):
        """Extend this template overwriting some blocks and properties and return new template.
        """
        assert all(isinstance(b, Block) for b in blocks), "Only instances of Block are accepted."
        assert all(b.name for b in blocks), "All extending blocks must have names."
        new_blocks = dict((b.name, b) for b in blocks)
        assert len(blocks) == len(new_blocks), "All blocks should have unique names."

        def copy(obj, blocks=None):
            if isinstance(obj, Node):
                if type(obj) == Block:
                    if obj.name in new_blocks:
                        block = copy(new_blocks.pop(obj.name), _find_blocks(obj))
                    else:
                        block = obj.__class__(**copy(obj.__dict__, blocks))
                        # change parent only for redefined blocks and their child blocks
                        if blocks is not None: 
                            block.parent = blocks.pop(obj.name, None)
                    return block
                return obj.__class__(**copy(obj.__dict__, blocks))
            elif isinstance(obj, dict):
                return dict((k, copy(v, blocks)) for k,v in obj.iteritems())
            elif hasattr(obj, '__iter__'):
                return obj.__class__(copy(i, blocks) for i in obj)
            else:
                return obj
        child = copy(self)
        assert not new_blocks, "Unknown blocks: %s" % new_blocks.keys()
        for k,v in kwargs.iteritems():
            setattr(child, k, v)
        return child

    def iterator(self, ctx=None):
        """
        Template can be compiled or just read before evaluation. In both cases
        evaluation are same (but the speed may be different) and this function hides from
        Template.eval read/preprocess/compile details.
        Compiled templates faster when same template rendered many times.
        Interpretered templates fatser in CGI-like environments, when a template rendered once.
        """
        return self.compile(ctx) if self.normalize else self.read(ctx)

    def _read_visitor(self):
        return preprocess_callable if self.preprocess else read_callable

    def walk_to_buffer(self, callable_visitor, obj, gen_func, ctx):
        buf = []
        gen = gen_func(buf)
        make_walker(callable_visitor, self.visitors, gen, ctx, self.indent_step)(obj)
        gen.close()
        return buf

    def read(self, ctx):
        """Apply read stage transformations to template nodes.
        """
        return self.walk_to_buffer(self._read_visitor(), self,\
                                   append_sent, ctx=None)

    def cache_key(self, ctx):
        """Return cache key for this template and context.
        By default return Template._default_cache_key but function can be redefined,
        and for example for different locales in context will be used different caches,
        so translation of templates will be done on compile stage.
        """
        return Template._default_cache_key

    def _get_cache(self):
        cache = getattr(self, '_cache', None)
        if cache is None:
            self._cache = cache = {}
        return cache

    def compile(self, ctx):
        """Normalize strings, resolve other issues that don't require ctx.
        """
        cache = self._get_cache()
        key = self.cache_key(ctx)
        if key not in cache:
            cache[key] = self.walk_to_buffer(self._read_visitor(), self, join_sent, ctx=None)
        return cache[key]

    def eval(self, ctx):
        """Expand all nodes and resolve all variables.
        """
        if self.normalize:
            return self.walk_to_buffer(execute_callable, self.compile(ctx), append_sent, ctx=ctx)
        else:
            return self.walk_to_buffer(execute_callable, self, append_sent, ctx=ctx)


    def render(self, ctx):
        """Evaluate template, join strings and optionaly encode result.
        @ctx - evaluation ctx of template (any dictionary can be passed).
        @encoding - if provided, encode result string with it, otherwise - return unicode. 
        """
        return u"".join(self.eval(ctx))

    def render_encoded(self, ctx, encoding='utf-8', errors='strict'):
        """Call render and encode result with provided encoding.
        """
        return self.render(ctx).encode(encoding, errors)

    def eval_list(self, param_list):
        """Replaces all callables in self.iterator() with corresponding values from params,
        the rest items converts to unicode.
        """
        params = iter(param_list)
        for item in self.iterator():
            if callable(item):
                yield unicode(params.next())
            else:
                yield unicode(item)

    def render_list(self, param_list):
        """Join strings from fast_eval to single unicode string.
        It's analog of python string.format with position arguments only.  Usefull for small
        nodes fragments with limited number of variables.
        """
        return u"".join(self.eval_list(param_list))

    def render_many_list(self, many_param_list):
        """Call fast_eval for each param_list from many_param_list and return resulting unicode.
        """
        return u"".join(chain(*(self.eval_list(param_list) for param_list in many_param_list)))


def render_list(nodes, data_source, normalize=True, indent_step=False):
    """Make template from nodes, rememember it in a closure and return renderer func.
    """
    t = Template(normalize=normalize, indent_step=indent_step) [nodes]
    def renderer(ctx):
        return t.render_list(data_source(ctx))
    return renderer

def render_many_list(nodes, data_source, normalize=True, indent_step=False):
    """Make template from nodes, rememember it in a closure and return renderer func.
    """
    t = Template(normalize=normalize, indent_step=indent_step) [nodes]
    def renderer(ctx):
        return t.render_many_list(data_source(ctx))
    return renderer

def visitor(*types):
    def wrapper(func):
        for t in types:
            DEFAULT_VISITORS[t] = func
        return func
    return wrapper


@visitor(Block)
def visit_block(walker, obj):
    walker.blocks.append(obj)          # remember block for Super resolving
    for i in obj.content:
        walker(i)
    walker.blocks.pop()

@visitor(_Super)
def visit_super(walker, obj):
    try:
        block = walker.blocks[-1]
    except IndexError:
        raise Exception("Super outside of a block.")
    else:
        parent = getattr(block, 'parent', None)
        if not parent:
            raise Exception("Super in block '%s' without parent." % getattr(block, 'name', ''))
        walker(parent)

def _maybe_attr(name, func):
    def _maybe_attr_check(ctx):
        res = func(ctx)
        return _attr(name, res) if res is not None else None
    return _maybe_attr_check

def _attr(name, value):
    return (u' ', name, u'="', value, '"')

def visit_attrs(walker, obj):
    for name, value in obj.iteritems():
        if callable(value) and not isinstance(value, Block):
            # postpone value check for runtime stage
            walker(_maybe_attr(name, value))
        elif value is not None:
            # walker(_attr(name, value))
            g = walker.emit_gen
            g.send(u' ')
            g.send(name)
            g.send(u'="')
            walker(value)
            g.send(u'"')

@visitor(Element)
def visit_element(walker, obj):
    g = walker.emit_gen
    g.send(u"<")
    g.send(obj.name)
    visit_attrs(walker, obj.attrs) 
    g.send(u">")
    for i in obj.content:
        walker(i)
    g.send(u"</")
    g.send(obj.name)
    g.send(u">")

@visitor(EmptyElement)
def visit_emptyelement(walker, obj):
    g = walker.emit_gen
    g.send(u"<")
    g.send(obj.name)
    visit_attrs(walker, obj.attrs)
    if obj.content:                # content is [""]
        g.send(u"></")
        g.send(obj.name)
        g.send(u">")
    else:
        g.send(u" />")

@visitor(Comment)
def visit_emptyelement(walker, obj):
    g = walker.emit_gen
    g.send(u"<!--")
    for i in obj.content:
        walker(i)
    g.send(u"-->")

@visitor(PI)
def visit_pi(walker, obj):
    g = walker.emit_gen
    g.send(u"<?")
    g.send(obj.name)
    visit_attrs(walker, obj.attrs)
    g.send(u"?>")

def indent_visit_element(walker, obj):
    g = walker.emit_gen
    walker.indent += 1
    g.send(u"<")
    g.send(obj.name)
    visit_attrs(walker, obj.attrs) 
    g.send(u">")
    for i in obj.content:
        walker(i)
    walker.indent -= 1
    g.send(u"</")
    g.send(obj.name)
    g.send(u">\n")

def enable_debug(template, indent_step=u' '*2):
    """Enable debug for template object ot class."""
    template.indent_step = indent_step
    template.visitors[Element] = indent_visit_element

# ------------------ private functions ---------------------

def _find_blocks(obj, blocks={}):
    """Return all blocks inside obj (including obj itself if it's block). """
    if type(obj) == Block:
        assert obj.name not in blocks, "Duplicated block name '%s' in %r" % (obj.name, blocks.keys())
        blocks[obj.name] = obj

    if isinstance(obj, Block):
        _find_blocks(obj.content, blocks)
    elif isinstance(obj, Node):
        _find_blocks(obj.__dict__, blocks)
    elif isinstance(obj, dict):
        [_find_blocks(v, blocks) for v in obj.itervalues()]
    elif hasattr(obj, '__iter__'):
        [_find_blocks(i, blocks) for i in obj]
    return blocks
