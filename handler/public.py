#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""不需要登录、也不走签名校验的公开入口：备案落地页和探活。

这里刻意不继承 BaseHandler：BaseHandler 的每个方法都要先过请求签名，
浏览器访问落地页、容器编排做探活都没有签名，走 BaseHandler 只会被拒绝。
"""
import json
import logging

from sqlalchemy import text
from tornado.web import RequestHandler

from util.database import engine
from util.redis_conn import redisConn

logger = logging.getLogger(__name__)

HTTP_OK = 200
HTTP_UNAVAILABLE = 503
HEALTH_DB_PROBE_SQL = text('SELECT 1')
COMPONENT_UP = 'up'
COMPONENT_DOWN = 'down'


class LandingHandler(RequestHandler):
    """备案落地页。"""

    def get(self, *args, **kwargs):
        self.render('index.html')


class HealthHandler(RequestHandler):
    """探活：MySQL 和 Redis 都能响应才算健康。只返回组件状态，不暴露地址和账号。"""

    def get(self, *args, **kwargs):
        components = {
            'mysql': self._probe(self._ping_mysql, 'mysql'),
            'redis': self._probe(self._ping_redis, 'redis'),
        }
        healthy = all(state == COMPONENT_UP for state in components.values())
        self.set_status(HTTP_OK if healthy else HTTP_UNAVAILABLE)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(json.dumps({'healthy': healthy, 'components': components}))

    @staticmethod
    def _ping_mysql():
        with engine.connect() as connection:
            connection.execute(HEALTH_DB_PROBE_SQL)

    @staticmethod
    def _ping_redis():
        redisConn.ping()

    @staticmethod
    def _probe(ping, name):
        try:
            ping()
        except Exception as exc:
            logger.error("健康检查失败 component=%s error=%s", name, type(exc).__name__)
            return COMPONENT_DOWN
        return COMPONENT_UP
