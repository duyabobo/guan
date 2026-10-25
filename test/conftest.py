#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""测试公共准备：不依赖真实 MySQL / Redis / 配置文件。

必须在任何业务模块 import 之前完成：
1. 写一份临时配置文件，让 util.config 能读到各个 section；
2. 把 redis.StrictRedis 换成 fakeredis，util.redis_conn 在 import 时拿到的就是内存实现。
"""
import os
import sys
import tempfile

import fakeredis
import pytest
import redis

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

_TEST_CONF = """
[global]
port=8888
server=offline
debug=false
cookie_secret=test
[mysql]
username=test
password=test
host=127.0.0.1
port=3306
database=test
[redis]
host=127.0.0.1
port=6379
[weixin]
appid=test_appid
secret=test_secret
"""

_conf_dir = tempfile.mkdtemp(prefix='guan-test-conf-')
_conf_prefix = os.path.join(_conf_dir, 'test')
with open(_conf_prefix + '.conf', 'w', encoding='utf-8') as _conf_file:
    _conf_file.write(_TEST_CONF)
os.environ['CONFNAME'] = _conf_prefix  # Configuration 会拼上 .conf

_fake_server = fakeredis.FakeServer()
redis.StrictRedis = lambda *args, **kwargs: fakeredis.FakeStrictRedis(server=_fake_server)


@pytest.fixture(autouse=True)
def _flush_fake_redis():
    """每个用例都从空 Redis 开始。"""
    fakeredis.FakeStrictRedis(server=_fake_server).flushall()
    yield
