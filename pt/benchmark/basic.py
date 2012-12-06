#! /usr/bin/env python
# encoding: utf-8
# Generate identical to http://genshi.edgewall.org/browser/trunk/examples/bench/basic.py template
# to compare time with other templates

from pt.benchmark import *

ctx = dict(title='Just a test', user='joe',
           items=['Number %d' % num for num in range(1, 15)])

if PtTemplate:
    def pt_template():
        header = div(id="header") [h1 [V("title")]]
        footer = div(id="footer")
        def greeting(name):
            return p [u"Hello, ", E(name)]
        def loop(ctx):
            if ctx['items']:
                enum = Enum(ctx['items'])
                return ul [(li(cls="last" if enum.last(i) else None) [item] for i, item in enum)]
        return PtTemplate() [html
                             [head [title [V("title")]]]
                             [body [header,
                                    F(greeting, S("user")),
                                    F(greeting, u"me"),
                                    F(greeting, u"world"),
                                    h2 ["Loop"], loop,
                                    footer]]]

    test_pt, test_pt_cgi = cached_and_cgi("pt", pt_template,
                                          lambda t: t.render(ctx))

if __name__ == '__main__':
    main("Basic template with blocks, if and loop", number=100)
    print pt_template().render(ctx)
