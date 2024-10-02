#! /usr/bin/env python
# -*- coding: utf-8 -*-


class C(object):
    def __init__(self, fn):
        print fn()

def f():
    return 'ff'


if __name__ == '__main__':
    C(f)
    C(lambda: "lambda")
