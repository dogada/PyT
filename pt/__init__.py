# -*- coding: utf-8 -*
# Copyright (c) 2010, Dmytro V. Dogadailo <entropyhacker@gmail.com>

__author__ = 'Dmytro V. Dogadailo <entropyhacker@gmail.com>'

"""
PyT - Python Templates

Advantages of Python Templates:
- transparent precompilation (i18n). Superior performance for localized templates.
- default formatters for different types
- all tags will be closed properly, i.e. avoid invalid <a name="id" />
- you can disable certain tags like <b> and force to use strong, or require some
- when template is split across small python function it's easy to write doctest for each tempate fragment and test all
"""

from pt.dom import *
from pt.ctx import *



