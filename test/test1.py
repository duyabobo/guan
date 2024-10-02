#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random

if __name__ == '__main__':
    a = [[str(random.randint(70,90)) for j in range(5)] for i in range(30)]
    b = ['\t'.join(i) for i in a]
    c = '\n'.join(b)
    with open('/Users/edy/Desktop/x.txt', 'wb') as f:
        f.write(c)
