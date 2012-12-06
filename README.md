PyT
===

### High-performance Python DSL for generation of (X)HTML with preprocessing and template inheritance.

There are some Python DSLs for generating HTML but they are useful only for dynamic (hence slow) generation of html. PyT DSL supports template inheritance and blocks, so you can extend base templates and redefine blocks inside templates like we do in full-featured template engines Jinja2, Mako, Django, etc.

In addition to this (and with Lisp in mind) PyT supports preprocessing or _compile time_ rules. For example, you can support 3 languages on an internationalized web-site, have own language environment and template cache for each supported language and _compile_ same template to unique for each environment form. In result, function calls like `gettext('Home')` will be resolved at _compile time_. At request time template will just  output already resolved internationalized strings.

Bellow is an example of PyT from `pt/demo/main.py`:

```python

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

def entry_detail():
    return (h3 [V("entry.name")],
            div ["rank: ", S("entry.rank", 0.0, format="%.2f"),
                 ", created: ", S("entry.created", format=short_date),
                 ", invalid: ", S("e.invalid", 0.107, format="%.2f")],
            p(cls=("entry ", V("entry.class")))[S("entry.content")])
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

ctx = dict(title=u"Hello world!",
           now=datetime.now(),
           entry={'name': 'Tips & tricks for <div> "layouts".', 'class': "hot",
                  'rank': 0.897, 'created': datetime.now(),
                  'content': '<p>html <b>tags</b></p>'},
           report=[(u"Name of %d" % i, u"Value > %d" % i) for i in xrange(3)],
           user = User("dogada"))

print EntryDetail.render(ctx)

```

Performance was the main goal for PyT and it runs quite well. The speed is comparable with fastest python template engines
Mako and Jinja2. You can test it yourself with script
```
user@host:PyT$ ./pt/benchmark/report.py
```
that compares results of rendering same template using PyT and Django, Mako, Jinja2, Genshi if they are available in
`PYTHONPATH`.

If you see error like `ImportError: No module named pt.demo.env`, please add `PyT` or current directory to `PYTHONPATH`:
```
user@host:PyT$ export PYTHONPATH=$PYTHONPATH:./
```

If you are interested in PyT, start with `./pt/demo/main.py` and then look at source code to understand how all this magic is
done.

The code is available under Simplified BSD License.

Have fun!
