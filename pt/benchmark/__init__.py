"""
Common for all tests functionality.
"""
import sys
import timeit

try:
    from pt.demo.env import *
    from pt.demo.env import Template as PtTemplate
except ImportError:
    PtTemplate = None

try:
    from django.conf import settings
    settings.configure()
    from django.template import Context as DjangoContext
    from django.template import Template as DjangoTemplate
except ImportError:
    DjangoContext = DjangoTemplate = None

try:
    from mako.template import Template as MakoTemplate
except ImportError:
    MakoTemplate = None

try:
    from jinja2 import Template as Jinja2Template
except ImportError:
    Jinja2Template = None

try:
    from genshi.builder import tag
    from genshi.template import MarkupTemplate, NewTextTemplate
except:
    MarkupTemplate = None


def cached_and_cgi(name, template_func, render):
    """Return 2 functions for testing template in cached and cgi modes."""
    _template = template_func()
    def test_cached():
        # reuse early created template
        render(_template)
    test_cached.__doc__ = "test_%s" % name
    def test_cgi():
        # create new template on each call
        render(template_func())
    test_cgi.__doc__ = "test_%s_cgi" % name
    return test_cached, test_cgi

def run(which=None, number=2):
    _test_module = sys.modules['__main__']
    tests = sorted([name for name in _test_module.__dict__.keys() \
                    if name.startswith('test_')])
    if which:
        tests = filter(lambda n: n[5:] in which, tests)
    for test in tests:
        t = timeit.Timer(setup='from __main__ import %s;' % test,
                         stmt='%s()' % test)
        time = t.timeit(number=number) / number

        if time < 0.00001:
            result = '   (not installed?)'
        else:
            result = '%16.2f ms' % (1000 * time)
        func = getattr(_test_module, test)
        print '%-35s %s' % (func.__doc__ or func.__name__, result)

def main(name, number=10):
    print "-"*len(name)
    print name
    print "-"*len(name)
    which = [arg for arg in sys.argv[1:] if arg[0] != '-']
    if '-p' in sys.argv:
        import cProfile, pstats
        prof = cProfile.Profile()
        prof.run('run(%r, number=1)' % which)
        stats = pstats.Stats(prof)
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(25)
        if '-v' in sys.argv:
            stats.print_callees()
            stats.print_callers()
    else:
        run(which, number)
