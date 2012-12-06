#!/usr/bin/env python

from timeit import Timer
import types

def adder(v1, v2):
    def add(v3):
        x = 4
        return v1 + v2 + v3 + x
    return add

class Add0(object):
    pass

class Add1(Add0):
    pass

class Add2(Add1):
    var = None

    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def __call__(self, v3):
        x = 4
        return self.v1 + self.v2 + v3 + x 

f1 = adder(1,2)
f2 = Add2(1,2)

visitors = {}
for t in (tuple, list, set, frozenset, xrange, types.GeneratorType):
    visitors[t] = f1

def getitem_test(t):
    return visitors[t]

def global_test(obj):
    return type(obj)

def closure_test():
    _type = type
    def closured(obj):
        return _type(obj)
    return closured

def run(name, timer, count=10000):
    print "%20s: %fms, count=%d" % (name, timer.timeit(count)*1000, count)

if __name__ == "__main__":
    print "Access to outer variables for 'func_closure' vs 'getattr'"
    run("f1 (closure)", Timer(setup="from __main__ import f1;", stmt='f1(5)'))
    run("f2 (getattr)", Timer(setup="from __main__ import f2;", stmt='f2(5)'))
    run("callable(f1)", Timer(setup="from __main__ import f1;", stmt='callable(f1)'))
    run("callable(f2)", Timer(setup="from __main__ import f2;", stmt='callable(f2)'))
    run("type(f1)", Timer(setup="from __main__ import f1", stmt='type(f1)'))
    run("type(f2)", Timer(setup="from __main__ import f2", stmt='type(f2)'))
    run("global_test", Timer(setup="from __main__ import global_test, f1", stmt='global_test(f1)'))
    run("closure_test", Timer(setup="from __main__ import closure_test, f1; cf=closure_test()", stmt='cf(f1)'))

    run("isinstance(f2, Add2)", Timer(setup="from __main__ import f2, Add2;", stmt='isinstance(f2, Add2)'))
    run("isinstance(f2, Add1)", Timer(setup="from __main__ import f2, Add1;", stmt='isinstance(f2, Add1)'))
    run("isinstance(f2, Add0)", Timer(setup="from __main__ import f2, Add0;", stmt='isinstance(f2, Add0)'))
    run("hasattr(obj, '__iter__')", Timer(setup="obj=[1,2];", stmt="hasattr(obj, '__iter__')"))
    run("getitem_test", Timer(setup="from __main__ import visitors; t=type([1,2]);", stmt='visitors[t]'))
    run("f2.v1", Timer(setup="from __main__ import f2;", stmt='f2.v1'))
    run("Add2.var", Timer(setup="from __main__ import Add2;", stmt='Add2.var'))
    run("f2.var", Timer(setup="from __main__ import f2;", stmt='f2.var'))
    run("x", Timer(setup="x=1;", stmt='x'))
    run("func(1)", Timer(setup="def func(x): pass", stmt='func(1)'))
    run("func(1,2)", Timer(setup="def func(x, y): pass", stmt='func(1, 2)'))
    run("func(1,2,3)", Timer(setup="def func(x, y, z): pass", stmt='func(1, 2, 3)'))
    run("func(x,y,z,*args, **kw)", Timer(setup="def func(x, y, z, *args, **kw): pass", stmt='func(1, 2, 3)'))
    run("func(*args)", Timer(setup="def func(*args): pass", stmt='func(1, 2, 3)'))
    run("func(**kw)", Timer(setup="def func(**kw): pass", stmt='func(x=1, y=2, z=3)'))
