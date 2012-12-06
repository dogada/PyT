# coding: utf-8

import sys
from time import time
from pt.demo.env import *
from pt.demo import i18n_stub as i18n
_ = Trans

def test():
    print Template()[div["Hello"]].render({})
    print Template()[div(cls="main")[br]].render({})
    print Template()[br].render({}), Template()[br[""]].render({})
    print Template()[meta(name="title", content="Sitemap", **{"xml:lang": "en", "http-equiv": 200})[""]].render({})
    print Template()[div[_(u'Hello, %(user)s!', user=u'Stas')]].render({})
    i18n.set_locale('ru')
    print Template()[p[i [_('Home')], _(u'Hello, %(user)s!', user=u'Стас')]].render({})
    t = Template()[p[i [_('Home')], b ["locale=", S("locale")], _(u'Hello, %(user)s!', user=S('user'))]]
    print t.render({'user': u'Стас', 'locale': i18n.locale})
    print t.render({'user': u'Дима', 'locale': i18n.locale})
    i18n.set_locale('en')
    print t.render({'user': u'Stas', 'locale': i18n.locale})
    print t.render({'user': u'Dima', 'locale': i18n.locale})
    i18n.set_locale('es')
    print t.render({'user': u'Pablo', 'locale': i18n.locale})
    print t.render({'user': u'Huan', 'locale': i18n.locale})

if __name__ == "__main__":
    test()
