#! /usr/bin/env python
# -*- coding: utf-8 -*-


def addParams(url, **kwargs):
    params = '&'.join(['{k}={v}'.format(k=k, v=v) for k, v in kwargs])
    if "?" in url:
        return "{url}&{params}".format(url=url, params=params)
    else:
        return "{url}?{params}".format(url=url, params=params)
