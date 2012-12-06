# coding: utf-8

"""
Dummy implementation of ugettext and translation for 'ru' locale.
"""

locale = 'en'

_translations = {
    'ru': {u'Home': u'Начало',
           u'Hello, %(user)s!': u'Привет, %(user)s!'},
    }

def set_locale(loc):
    global locale
    locale = loc


def ugettext(message, **params):
    """Dummy ugettext impl.
    >>> set_locale('en')
    >>> ugettext(u'Home')
    u'Home'
    >>> ugettext(u'New feature')  # untranslated text
    u'New feature'
    >>> set_locale('ru')
    >>> ugettext(u'Home')
    u'\u041d\u0430\u0447\u0430\u043b\u043e'
    >>> ugettext(u'Hello, %(user)s!', user=u'\u0421\u0442\u0430\u0441')
    u'\u041f\u0440\u0438\u0432\u0435\u0442, \u0421\u0442\u0430\u0441!'
    >>> set_locale('fr')                   # locale without transaltion
    >>> print ugettext(u'Home')
    Home
    """
    _trans = _translations.get(locale, {}).get(message, message)
    return _trans % params if params else _trans

if __name__ == "__main__":
    import doctest
    doctest.testmod()
