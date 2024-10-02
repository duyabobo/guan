#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import time


def getRandomStr(seed):
    t = time.time()
    return hashlib.md5(str(t) + str(seed)).hexdigest()
