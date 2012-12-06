#! /usr/bin/env python
# coding: utf-8

import sys
from time import time
from pt.demo.env import *

_ = Trans

def url(name, *args, **kw):
    return u"/%s/" % name

class User(object):
    def __init__(self, username):
        self.username = username

short_date = lambda date: date.strftime("%Y-%m-%d")

def header():
    return head [
        title [V("title")],
        meta(name="title", content=V("title")),
        meta(name="keywords", content=Block("keywords") ["python, xml, html, template"])]

def menu():
    logout_url = url("logout")
    def user_menu(ctx):
        user = ctx['user']
        if user:
            # test of dynamic generator that yields tuple
            yield li [a(href=url("profile_home", user.username)) [user.username]],\
                  li [a(href=logout_url, cls=Maybe("active", S("user"))) ["logout"]]
        else:
            yield li ["login"]
    return ul(cls="menu") [
        li [a(href="/") [_("Home")]],
        user_menu,
        li [a(href="/about/") ["About"]]]

def report():
    row = Template() [tr [td[S("i")], td[V("name")], td[V("value")]]] #.normalize()
    def rows(ctx):
        return u"".join([row.render(dict(i=i,name=name, value=value)) for i, (name, value) in enumerate(ctx['report'])])
    return table [tr [th ["#"], th ["Name"], th ["Value"]], rows]

def entry_detail():
    return (h3 [V("entry.name")],
            div ["rank: ", S("entry.rank", 0.0, format="%.2f"),
                 ", created: ", S("entry.created", format=short_date),
                 ", invalid: ", S("e.invalid", 0.107, format="%.2f")],
            p(cls=("entry ", V("entry.class")))[S("entry.content")])


def test():
    return Comment ['not escaped <p id="myid"> & <br />,y escaped: --, title=', V("title")],\
           '\n<p xml:lang="ua">Raw html</p>\n'

Base = Template() [
    PI.xml(version="1.0", encoding="utf-8"),
    '\n<!DOCTYPE xhtml>\n',
    html [
        Block("header") [header()],
        body(id="main_id", cls="main") [
            Block("body") [
                Block("menu") [menu()],
                Block("content") [""],
                Block("footer") [small ["Generated at: ", DateTime("now")]]]
        ]]]

EntryDetail = Base.extend([
    Block("keywords") [Super, ", entry"],
    Block("content") [entry_detail()],
    Block("footer") [Super, test(), Super]], debug=True)

Report = EntryDetail.extend([
    Block("keywords") [Super, ", report"],
    Block("content") [report()],
    Block("footer") [""]])

Extra = Report.extend([
    Block("body") [
        Block("menu") [Super],
        Block("content") [h1 ["Redefined body block with new content block and parent menu blocks."]],
    ]])

from datetime import datetime
ctx = dict(title=u"Hello world!",
           now=datetime.now(),
           entry={'name': 'Tips & tricks for <div> "layouts".', 'class': "hot",
                  'rank': 0.897, 'created': datetime.now(),
                  'content': '<p>html <b>tags</b></p>'},
           report=[(u"Name of %d" % i, u"Value > %d" % i) for i in xrange(3)],
           user = User("dogada"))
DELIM = "-"*40

def render_base():
    print Base.render(ctx)

def full_doc(output=True):
    for t in (Base, EntryDetail, Report):
        res = t.render(ctx)
        if output:
            print DELIM
            print res

def extra_doc():
    # full_doc is used for performance monitoring, so better don't change it
    # new test should be added to Extra
    print DELIM
    print Extra.render(ctx)

PASS_COUNT = 2

def _benchmark(name, templates, ctx):
    for t in templates:
        if t.normalize:
            t.render(ctx)                  # force compilation
    print name,
    for t in templates:
        elapsed = 0.0
        for x in xrange(PASS_COUNT):
            start = time()
            res = t.render(ctx)
            elapsed += (time() - start)
        print "%s=%.4f, %db" % (t.name, elapsed/PASS_COUNT, len(res)),
    print

def benchmark():
    benchmark_report()

def benchmark_report():
    ctx = dict(title=u"Hello world!", user = User("dogada"))
    def add_report(total):
        ctx['report']  = [(u"Name of %d" % i, u"Value > %d" % i) for i in xrange(total)]
        return ctx

    def _run(name, templates):
        for total in 0, 10, 100:
            _benchmark(name + str(total), templates, add_report(total))

    compiled = Report.extend(name="compiled", normalize=True, debug=False)
    cgi = Report.extend(name="cgi", normalize=False, debug=False)
    debug = Report.extend(name="debug", normalize=True, debug=True)
    templates = [compiled, cgi, debug]
    _run("static_report", templates)
    # print cgi.render(add_report(10))

    def fast_report():
        header = tr [th ["#"], th ["Name"], th ["Value"]]
        row = tr [td[S("#")], td [V("N")], td[V("V")]]
        def rows_data(ctx):
            return ((i, E(name), E(value)) for i, (name, value) in enumerate(ctx['report']))
        return table [header, render_many_list(row, rows_data)]

    templates = [t.extend([Block("content") [fast_report()]]) for t in templates]
    _run("fast_report", templates)

    def dynamic_report():
        def rows(ctx):
            for i, (name, value) in enumerate(ctx['report']):
                yield tr [td[i], td[E(name)], td[E(value)]]
        return table [tr [th ["#"], th ["Name"], th ["Value"]], rows]
    templates = [t.extend([Block("content") [dynamic_report()]]) for t in templates]
    _run("dynamic_report", templates)


if __name__ == "__main__":
    if '-t' in sys.argv:
        import doctest
        doctest.testmod()
    elif '-p' in sys.argv:
        import cProfile, pstats
        prof = cProfile.Profile()
        prof.run('full_doc(output=False)')
        stats = pstats.Stats(prof)
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
        if '-v' in sys.argv:
            stats.print_callees()
            stats.print_callers()
    else:
        full_doc()
        extra_doc()
        if '-b' in sys.argv:
            benchmark()
