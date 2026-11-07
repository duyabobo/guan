#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from handler import public


class HealthHandlerTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application([(r'/health$', public.HealthHandler)])

    def test_healthy_when_mysql_and_redis_respond(self):
        original = public.HealthHandler._ping_mysql
        public.HealthHandler._ping_mysql = staticmethod(lambda: None)
        try:
            response = self.fetch('/health')
        finally:
            public.HealthHandler._ping_mysql = original
        body = json.loads(response.body)
        assert response.code == 200
        assert body == {'healthy': True, 'components': {'mysql': 'up', 'redis': 'up'}}

    def test_unhealthy_when_mysql_down(self):
        def broken():
            raise ConnectionError('secret-host:3306 refused')

        original = public.HealthHandler._ping_mysql
        public.HealthHandler._ping_mysql = staticmethod(broken)
        try:
            response = self.fetch('/health')
        finally:
            public.HealthHandler._ping_mysql = original
        body = json.loads(response.body)
        assert response.code == 503
        assert body['components']['mysql'] == 'down'
        assert 'secret-host' not in response.body.decode()  # 不把内部地址泄露给探活方
