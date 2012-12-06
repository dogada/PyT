#! /usr/bin/env python
# encoding: utf-8


"""
Test small template with 2 variables.
"""

from pt.benchmark import *

ctx = {'name': 'Hello world',
       'content': 'Where we will be when the summer will gone?'}

if PtTemplate:
    def pt_template():
        return PtTemplate() [html [body [h1 [V("name")],
                                         p [V("content")]]]]

    test_pt, test_pt_cgi = cached_and_cgi("pt", pt_template,
                                          lambda t: t.render(ctx))

if DjangoTemplate:
    def django_tmpl():
        return DjangoTemplate(
"""
<html>
<body>
<h1>{{ name }}</h1>
<p>{{ value }}</p>
</body>
</html>
""")
    test_django, test_django_cgi = cached_and_cgi("django", django_tmpl,
                                                   lambda t: t.render(DjangoContext(ctx)))

if Jinja2Template:
    def jinja2_tmpl():
        return Jinja2Template(
"""
<html>
<body>
<h1>{{ name|e }}</h1>
<p>{{ content|e }}</p>
</body>
</html>
""")
    test_jinja2, test_jinja2_cgi = cached_and_cgi("jinja2", jinja2_tmpl,
                                                   lambda t: t.render(ctx))

if MakoTemplate:
    def mako_tmpl():
        return MakoTemplate("""
<html>
<body>
<h1>${name|h }</h1>
<p>${content|h }</p>
</body>
</html>
""")
    test_mako, test_mako_cgi = cached_and_cgi("mako", mako_tmpl, lambda t: t.render(**ctx))

if __name__ == '__main__':
    main("Tiny template with 2 variables", number=100)
