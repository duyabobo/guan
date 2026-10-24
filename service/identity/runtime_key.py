#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""真实 unionid 只存在于 Redis。数据库里的封存值解不开它。"""
import logging

from service.sensitive.purpose import purpose_accepted
from util.const.identity import RUNTIME_UNION_KEY, RUNTIME_UNION_TTL_SEC
from util.redis_conn import decode_redis_value, redisConn

logger = logging.getLogger(__name__)


def put_unionid(passport_id, unionid):
    if not passport_id or not unionid:
        logger.error("拒绝写入空的运行时身份密钥 passport=%s", passport_id)
        return False
    redisConn.set(_key(passport_id), unionid, ex=RUNTIME_UNION_TTL_SEC)
    logger.info("运行时身份密钥已写入 passport=%s", passport_id)
    return True


def has_unionid(passport_id):
    if not passport_id:
        return False
    return bool(redisConn.exists(_key(passport_id)))


def touch_unionid(passport_id):
    if passport_id:
        redisConn.expire(_key(passport_id), RUNTIME_UNION_TTL_SEC)


def material_for(passport_id, purpose):
    found = materials_for([passport_id], purpose)
    return found.get(int(passport_id or 0), '')


def materials_for(passport_ids, purpose):
    """一次取回。调用方必须带用途。值不写日志。"""
    if not purpose_accepted(purpose):
        logger.error("拒绝无用途读取运行时身份密钥")
        return {}
    ids = _unique_ids(passport_ids)
    if not ids:
        return {}
    logger.info("读取运行时身份密钥 purpose=%s count=%s", purpose.strip(), len(ids))
    values = redisConn.mget([_key(passport_id) for passport_id in ids])
    found = {}
    for passport_id, value in zip(ids, values):
        text = decode_redis_value(value)
        if text:
            found[passport_id] = text
    return found


def _unique_ids(passport_ids):
    ids = []
    seen = set()
    for passport_id in passport_ids or []:
        if not passport_id:
            continue
        number = int(passport_id)
        if number in seen:
            continue
        seen.add(number)
        ids.append(number)
    return ids


def _key(passport_id):
    return RUNTIME_UNION_KEY % int(passport_id)
