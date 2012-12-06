"""
Utility functions.
"""

def coroutine(func):
    def starter(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr
    return starter

@coroutine
def append_sent(buf):
    """Append sent values into buf."""
    while True:
        buf.append((yield))

@coroutine
def join_sent(buf):
    """Join sent strings and append into buf."""
    prev = []
    try:
        while True:
            obj = (yield)
            if isinstance(obj, basestring):
                prev.append(obj)
            else:
                if prev:
                    buf.append(u"".join(prev))
                    prev = []
                buf.append(obj)
    finally:                            # handle GeneratorExit
        if prev:
            buf.append(u"".join(prev))


def join_strings(stream):
    """Join string sequences in the stream into single unicode string.
    """
    buf = []
    for i in stream:
        if isinstance(i, basestring):
            buf.append(i)
        else:
            if buf:
                yield u"".join(buf)
                buf = []
            yield i
    if buf:
        yield u"".join(buf)

def debug(func):
    """Print function call with params and result."""
    def debugged(*args, **kwargs):
        res = func(*args, **kwargs)
        _args = ",".join(args)
        _kw = ",".join("%s=%r" % (k, v) for k, v in  kwargs.iteritems())
        if _args and _kw:
            _kw = "," + _kw
        print "debug: %s(%s%s) -> %r" % (func.__name__, _args, _kw, res)
        print
        return res
    debugged.__name__ = func.__name__
    return debugged
