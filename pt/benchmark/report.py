#! /usr/bin/env python
# encoding: utf-8 

"""
Generate a report from 100 rows and 10 columns as HTML table. All values are escaped.
"""

from pt.benchmark import *

report = [dict(("name #%d" % col, "value #%d" % col) for col in xrange(10)) for row in xrange(100)]
ctx = {'report': report}

if PtTemplate:
    def pt_template():
        def rows_data(ctx):
            return (map(E, row.values()) for row in ctx['report'])
        return PtTemplate() [table [render_many_list(tr [[td[S("")] for i in report[0]]], rows_data)]]

    test_pt, test_pt_cgi = cached_and_cgi("pt", pt_template,
                                           lambda t: t.render(ctx))

    def test_pt_nocache():
        """PT without caching (yield all tags)."""
        t = PtTemplate(normalize=False) [table [(tr [(td [E(c)] for c in row.values())] \
                                  for row in report)]]
        t.render({})

if DjangoTemplate:
    def django_tmpl():
        return DjangoTemplate("""
<table>
{% for row in report %}
<tr>{% for col in row.values %}{{ col|escape }}{% endfor %}</tr>
{% endfor %}
</table>
""")
    test_django, test_django_cgi = cached_and_cgi("django", django_tmpl,
                                                   lambda t: t.render(DjangoContext(ctx)))

if Jinja2Template:
    def jinja2_tmpl():
        return Jinja2Template("""
<table>
{% for row in report %}
<tr>{% for col in row.values() %}{{ col|escape }}{% endfor %}</tr>
{% endfor %}
</table>
""")
    test_jinja2, test_jinja2_cgi = cached_and_cgi("jinja2", jinja2_tmpl,
                                                   lambda t: t.render(ctx))

if MakoTemplate:
    def mako_tmpl():
        return MakoTemplate("""
<table>
% for row in report:
<tr>
% for col in row.values():
<td>${ col |h  }</td>
% endfor
</tr>
% endfor
</table>
""")
    test_mako, test_mako_cgi = cached_and_cgi("mako", mako_tmpl, lambda t: t.render(**ctx))

if MarkupTemplate:
    genshi_tmpl = MarkupTemplate("""
    <table xmlns:py="http://genshi.edgewall.org/">
    <tr py:for="row in report">
    <td py:for="c in row.values()" py:content="c"/>
    </tr>
    </table>
    """)

    genshi_tmpl2 = MarkupTemplate("""
    <table xmlns:py="http://genshi.edgewall.org/">$report</table>
    """)

    genshi_text_tmpl = NewTextTemplate("""
    <table>
    {% for row in report %}<tr>
    {% for c in row.values() %}<td>$c</td>{% end %}
    </tr>{% end %}
    </table>
    """)

    def test_genshi():
        """Genshi template"""
        stream = genshi_tmpl.generate(report=report)
        stream.render('html', strip_whitespace=False)

    def test_genshi_text():
        """Genshi text template"""
        stream = genshi_text_tmpl.generate(**ctx)
        stream.render('text')

    def test_genshi_builder():
        """Genshi template + tag builder"""
        stream = tag.TABLE([
            tag.tr([tag.td(c) for c in row.values()])
            for row in report
        ]).generate()
        stream = genshi_tmpl2.generate(report=stream)
        stream.render('html', strip_whitespace=False)

    def test_builder():
        """Genshi tag builder"""
        stream = tag.TABLE([
            tag.tr([
                tag.td(c) for c in row.values()
            ])
            for row in report
        ]).generate()
        stream.render('html', strip_whitespace=False)


if __name__ == '__main__':
    main("Generating 100x10 table with escaping", number=20)
