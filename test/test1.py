#! /usr/bin/env python
# -*- coding: utf-8 -*-

class C(object):
    def __enter__(self):
        print '__enter__'

    def __exit__(self, exc_type, exc_val, exc_tb):
        print '__exit__'

    def enter(self):
        print 'enter'

    def exit(self):
        print 'exit'


if __name__ == '__main__':
    with C():
        print 'with'
