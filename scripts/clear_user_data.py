#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""清空账号、资料、见面，以及还留在 Redis 里的登录态。

地区和地点不动。SERVER_ENV=online 时直接退出。
不会重写演示数据。要连演示数据一起重灌，用 scripts/init_db.py --reset-demo。

用法:
  python scripts/clear_user_data.py
  docker-compose exec app python scripts/clear_user_data.py
"""
import logging
import os
import sys

import pymysql

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from service.common.phone_number import (
    PHONE_CODE_KEY,
    PHONE_GAP_NUMBER_KEY,
    PHONE_GAP_PASSPORT_KEY,
    PHONE_TRY_KEY,
)
from util.const.identity import RUNTIME_UNION_KEY, SESSION_KEY_PREFIX
from util.const.notice import ONLINE_SERVER, PASSPORT_LOC_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 账号和见面。地点、省市区不在这里。
USER_DATA_TABLES = (
    'notice_sent',
    'subscribe_grant',
    'sensitive_record',
    'activity_change_record',
    'activity_seat',
    'share',
    'profile_attr',
    'activity',
    'passport',
)
_MISSING_TABLE = 1146
_SCAN_COUNT = 200
_LIST_CACHE_GLOB = 'GuanguanService:*'
_MEET_LOCK_GLOB = 'activityOprete:*'
_RATE_GLOBS = ('unique:*', 'failed_cnt:*', 'success_cnt:*')


def _glob_from_template(template):
    if '%s' in template:
        return template.replace('%s', '*')
    return template + '*'


USER_REDIS_GLOBS = (
    _glob_from_template(RUNTIME_UNION_KEY),
    _glob_from_template(SESSION_KEY_PREFIX),
    _glob_from_template(PHONE_CODE_KEY),
    _glob_from_template(PHONE_GAP_PASSPORT_KEY),
    _glob_from_template(PHONE_GAP_NUMBER_KEY),
    _glob_from_template(PHONE_TRY_KEY),
    _glob_from_template(PASSPORT_LOC_KEY),
    _LIST_CACHE_GLOB,
    _MEET_LOCK_GLOB,
) + _RATE_GLOBS


def refuse_if_online(server_env):
    """线上库一旦清空，账号和见面都没了。"""
    if server_env == ONLINE_SERVER:
        raise SystemExit('SERVER_ENV=online，拒绝清空用户数据')


def truncate_user_tables(conn):
    """丢掉账号、资料、见面。表不存在就跳过。地点表不动。"""
    removed = 0
    with conn.cursor() as cur:
        cur.execute('SET FOREIGN_KEY_CHECKS = 0')
        try:
            removed = _truncate_each(cur)
        finally:
            cur.execute('SET FOREIGN_KEY_CHECKS = 1')
    conn.commit()
    logger.info('  [清空] 用户与见面表 %d 张', removed)
    return removed


def _truncate_each(cur):
    removed = 0
    for table in USER_DATA_TABLES:
        try:
            cur.execute('TRUNCATE TABLE `%s`' % table)
        except pymysql.err.DatabaseError as exc:
            if exc.args and exc.args[0] == _MISSING_TABLE:
                logger.info('  [跳过] 表不存在 %s', table)
                continue
            raise
        removed += 1
    return removed


def clear_user_redis(client):
    """删掉还能代表这些用户的会话、身份密钥和验证码。"""
    deleted = 0
    for pattern in USER_REDIS_GLOBS:
        keys = list(client.scan_iter(match=pattern, count=_SCAN_COUNT))
        if not keys:
            continue
        deleted += client.delete(*keys)
    logger.info('  [清空] Redis 用户键 %d 个', deleted)
    return deleted


def wipe_user_state(conn, redis_client):
    """先清登录态。Redis 失败就不动表，避免账号没了会话还在。"""
    clear_user_redis(redis_client)
    return truncate_user_tables(conn)


def main():
    from init_db import _connect, _load_env_file, _redis_client

    _load_env_file()
    refuse_if_online(os.environ.get('SERVER_ENV', ''))
    redis_client = _redis_client()
    conn = _connect()
    try:
        wipe_user_state(conn, redis_client)
    finally:
        conn.close()
    logger.info('=== 用户数据已清空，地区和地点仍在 ===')


if __name__ == '__main__':
    main()
