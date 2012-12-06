"""
Default PYXT environment, usually each project have own with all required by templates imports.
"""
from datetime import datetime

import pt
from pt.xhtml import *
from pt import Template as DefaultTemplate, Block, Var as V, SafeVar as S, Function as F, \
     CtxRef, Super, Enum, Maybe, UNDEFINED
from pt import preprocess, resolve_kwargs, render_list, render_many_list, enable_debug
from pt.utils import debug

class Template(DefaultTemplate):
    def cache_key(self, ctx):
        """Use own cache for each locale. If not use default key.
        """
        return ctx.get('locale', '')

#enable_debug(Template)
E = pt.xml_escape

from pt.demo import i18n_stub

def Trans(message, _gettext=i18n_stub.ugettext, **params):
    """Return gettext caller marked with preprocess flag.
    """
    if params:
        # 2 stages: on preprocessor stage translate message, on runtime stage - apply params
        def gettext_params(ctx):
            translated_message = _gettext(message)
            return lambda ctx: translated_message % resolve_kwargs(ctx, params)
        return preprocess(gettext_params)
    else:
        return preprocess(lambda ctx: _gettext(message))

_ = Trans                               # shortcut for i18n access

def DateTime(name_or_value, default=UNDEFINED, format=lambda v: v.strftime("%Y-%m-%d %H:%M:%S")):
    """Format datetime. Accepts both variable name and datetime as first param.
    """
    if isinstance(name_or_value, datetime):
        return format(name_or_value)
    return V(name_or_value, default, format, False)
