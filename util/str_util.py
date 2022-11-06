#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import time


def getRandomStr():
    t = time.time()
    return hashlib.md5(str(t)).hexdigest()
