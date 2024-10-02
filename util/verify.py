#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random


def generate_code():
    return '%04d' % random.randint(0, 10000)
