#! /usr/bin/env python
# -*- coding: utf-8 -*-


def getTokenKey():
    return "wx:miniprogram:accesstoken"


def getToken(redis):
    key = getTokenKey()
    return redis.get(key)


def setToken(redis, token):
    key = getTokenKey()
    return redis.set(key, token, ex=7200)
