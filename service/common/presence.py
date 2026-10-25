#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""最近一次打开列表的坐标，以及是不是已经好几天没来。"""
import logging

from util.const.identity import RUNTIME_UNION_KEY, RUNTIME_UNION_TTL_SEC
from util.const.match import LATITUDE_MAX, LATITUDE_MIN, LONGITUDE_MAX, LONGITUDE_MIN
from util.const.notice import PASSPORT_LOC_KEY, REACTIVATE_IDLE
from util.redis_conn import decode_redis_value, redisConn

logger = logging.getLogger(__name__)

_LOC_TTL_SEC = RUNTIME_UNION_TTL_SEC


def remember_location(passport_id, latitude, longitude):
    if not passport_id:
        return
    if not _inside(latitude, longitude):
        logger.info("用户位置未记下 passport=%s 坐标超出范围", passport_id)
        return
    redisConn.set(PASSPORT_LOC_KEY % int(passport_id), '%.6f,%.6f' % (latitude, longitude), ex=_LOC_TTL_SEC)
    logger.info("已记下用户位置 passport=%s", passport_id)


def locations_of(passport_ids):
    ids = _ids(passport_ids)
    if not ids:
        return {}
    values = redisConn.mget([PASSPORT_LOC_KEY % passport_id for passport_id in ids])
    found = {}
    for passport_id, value in zip(ids, values):
        point = _parse_point(decode_redis_value(value))
        if point:
            found[passport_id] = point
    return found


def idle_passport_ids(passport_ids):
    """每次已登录请求都会把 unionid 的过期时间拨回满额。剩余寿命变短，就是这段时间没来。"""
    ids = _ids(passport_ids)
    if not ids:
        return []
    pipe = redisConn.pipeline()
    for passport_id in ids:
        pipe.pttl(RUNTIME_UNION_KEY % passport_id)
    remains = pipe.execute()
    idle_after = REACTIVATE_IDLE.total_seconds()
    idle = []
    for passport_id, remain_ms in zip(ids, remains):
        if _quiet_seconds(remain_ms) >= idle_after:
            idle.append(passport_id)
    logger.info("沉默用户 scanned=%s idle=%s", len(ids), len(idle))
    return idle


def _quiet_seconds(remain_ms):
    if remain_ms is None:
        return 0
    remain_ms = int(remain_ms)
    if remain_ms < 0:
        return 0
    return RUNTIME_UNION_TTL_SEC - (remain_ms / 1000.0)


def _ids(passport_ids):
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


def _inside(latitude, longitude):
    if latitude is None or longitude is None:
        return False
    return LATITUDE_MIN <= latitude <= LATITUDE_MAX and LONGITUDE_MIN <= longitude <= LONGITUDE_MAX


def _parse_point(text):
    if not text or ',' not in text:
        return None
    lat_text, lng_text = text.split(',', 1)
    try:
        latitude = float(lat_text)
        longitude = float(lng_text)
    except ValueError:
        return None
    if not _inside(latitude, longitude):
        return None
    return latitude, longitude
