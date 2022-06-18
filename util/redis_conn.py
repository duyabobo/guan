#! /usr/bin/env python
# -*- coding: utf-8 -*-
from redis import StrictRedis
import util.config

redisConn = StrictRedis(util.config.get('redis', 'host'), util.config.get('redis', 'port'))
