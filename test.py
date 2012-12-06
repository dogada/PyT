#! /usr/bin/env python

import pt
from pt import dom, ctx

if __name__ == "__main__":
    import doctest
    for m in (pt, dom, ctx):
        doctest.testmod(m)
