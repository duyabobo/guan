#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

from util.encode import md5_hex


def getRandomStr(seed):
    t = time.time()
    return md5_hex(str(t) + str(seed))
