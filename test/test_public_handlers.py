#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from handler import public
from util.startup_check import WEAK_SECRETS, find_config_problems


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


def test_startup_check_flags_weak_and_missing_secrets(monkeypatch):
    values = {('mysql', 'password'): 'guan123', ('redis', 'password'): '', ('weixin', 'secret'): 'real-secret'}
    monkeypatch.setattr('util.startup_check.util.config.get_optional', lambda sect, opt, default='': values[(sect, opt)])
    problems = find_config_problems()
    assert len(problems) == 2
    assert any('mysql' in p for p in problems)
    assert any('redis' in p for p in problems)


def test_startup_check_passes_with_real_secrets(monkeypatch):
    monkeypatch.setattr('util.startup_check.util.config.get_optional', lambda sect, opt, default='': 'a-long-random-value')
    assert find_config_problems() == []
    assert '' in WEAK_SECRETS
