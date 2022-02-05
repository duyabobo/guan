#! /usr/bin/env python
# -*- coding: utf-8 -*-

class BaseService(object):
    def __init__(self, dbSession, redis):
        self.dbSession = dbSession
        self.redis = redis
