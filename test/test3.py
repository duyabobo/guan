#! /usr/bin/env python
# -*- coding: utf-8 -*-

class C(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def z(self):
        return 'z'

    def __getattribute__(self, name):
        print '__getattribute__, name=%s' % name
        return super(C, self).__getattribute__(name)

    def __getattr__(self, item):
        print '__getattr__, item=%s' % item
        return super(C, self).__getattr__(item)

    def __setattr__(self, key, value):
        print '__setattr__ key=%s, value=%s' % (key, value)
        return super(C, self).__setattr__(key, value)


if __name__ == '__main__':
    c = C(1, 2)
    print c.x
    print c.y
    print c.z
    c.w = 'w'
    print c.w
    print c.u
