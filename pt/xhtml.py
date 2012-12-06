"""
XHTML tags.


TODO:
- globals() instead exec?

"""
import pt

_non_empty_html_tags = '''
  a abbr acronym address applet b bdo big blockquote body button
  caption center cite code colgroup dd dfn div dl dt em fieldset font
  form frame frameset h1 h2 h3 h4 h5 h6 head html i iframe ins kbd label
  legend li menu noframes noscript ol optgroup option p pre q s samp
  select small span strike strong style sub sup table tbody td
  textarea tfoot th thead title tr tt u ul var'''.split()


# http://www.w3.org/TR/xhtml1/#h-4.3
# All elements other than those declared in the DTD as EMPTY must have an end tag. Elements that are declared in the DTD
# as EMPTY can have an end tag or can use empty element shorthand.
# Empty element cannot contain text or other elements.

_maybe_empty_html_tags = '''
    area base br col hr img input link meta param'''.split()

for tag in _non_empty_html_tags:
    exec "%s = pt.Element(\"%s\")" % (tag, tag)

for tag in _maybe_empty_html_tags:
    exec "%s = pt.EmptyElement(\"%s\")" % (tag, tag)

script = pt.Element("script")
Comment = pt.Comment("")
class PI:
    xml = pt.PI(u"xml")
