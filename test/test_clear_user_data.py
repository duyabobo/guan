#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

import fakeredis
import pymysql
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import clear_user_data
from util.const.notice import ONLINE_SERVER


class _Cursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql):
        self.conn.statements.append(sql)
        if not sql.startswith('TRUNCATE'):
            return
        if self.conn.boom and self.conn.boom in sql:
            raise pymysql.err.DatabaseError(1290, 'refused')
        for name in self.conn.missing:
            if '`%s`' % name in sql:
                raise pymysql.err.DatabaseError(1146, 'missing')


class _Conn:
    def __init__(self, missing=(), boom=''):
        self.statements = []
        self.commits = 0
        self.missing = missing
        self.boom = boom

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1


def test_online_refuses():
    with pytest.raises(SystemExit, match='拒绝清空用户数据'):
        clear_user_data.refuse_if_online(ONLINE_SERVER)


def test_offline_is_allowed():
    clear_user_data.refuse_if_online('')
    clear_user_data.refuse_if_online('offline')


def test_truncate_keeps_places_and_commits():
    conn = _Conn()
    removed = clear_user_data.truncate_user_tables(conn)
    truncated = [sql for sql in conn.statements if sql.startswith('TRUNCATE')]
    assert removed == len(clear_user_data.USER_DATA_TABLES)
    assert truncated == ['TRUNCATE TABLE `%s`' % name for name in clear_user_data.USER_DATA_TABLES]
    assert 'region' not in clear_user_data.USER_DATA_TABLES
    assert 'address' not in clear_user_data.USER_DATA_TABLES
    assert conn.statements[0] == 'SET FOREIGN_KEY_CHECKS = 0'
    assert conn.statements[-1] == 'SET FOREIGN_KEY_CHECKS = 1'
    assert conn.commits == 1


def test_missing_table_is_skipped():
    conn = _Conn(missing=('identity_secret', 'subscribe_grant'))
    removed = clear_user_data.truncate_user_tables(conn)
    assert removed == len(clear_user_data.USER_DATA_TABLES) - 1
    assert conn.commits == 1


def test_truncate_error_restores_foreign_key_checks():
    conn = _Conn(boom='activity')
    with pytest.raises(pymysql.err.DatabaseError):
        clear_user_data.truncate_user_tables(conn)
    assert conn.commits == 0
    assert conn.statements[-1] == 'SET FOREIGN_KEY_CHECKS = 1'


def test_redis_drops_user_keys_only():
    client = fakeredis.FakeStrictRedis()
    client.set('runtime_union:7', 'union')
    client.set('accessToken:v2:abc', 'session')
    client.set('phone_bind:7', 'code')
    client.set('passport_loc:7', '1,2')
    client.set('GuanguanService:1:2:3', '[]')
    client.set('wx_mini_access_token', 'app-token')
    deleted = clear_user_data.clear_user_redis(client)
    assert deleted == 5
    assert client.get('wx_mini_access_token') == b'app-token'
    assert client.get('runtime_union:7') is None
    assert client.get('accessToken:v2:abc') is None
