#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

import pytest

from ral.cache import checkCache, lock
from util.redis_conn import redisConn


class _Activity(object):
    """锁和缓存的键从 self 的属性里取值。"""

    def __init__(self, activityId):
        self.activityId = activityId
        self.calls = 0

    @lock("lock:activity:{activityId}", failRet='busy')
    def locked_work(self, hold=None):
        self.calls += 1
        if hold:
            hold()
        return 'done'

    @lock("lock:activity:{activityId}", failRet='busy')
    def failing_work(self):
        raise RuntimeError('boom')

    @checkCache("cache:activity:{activityId}")
    def load(self):
        self.calls += 1
        return [1, 2, 3]

    @checkCache("cache:activity-bad:{activityId}")
    def load_unserializable(self):
        return {1, 2, 3}


def test_lock_runs_and_releases():
    activity = _Activity(1)
    assert activity.locked_work() == 'done'
    assert redisConn.get("lock:activity:1") is None
    assert activity.locked_work() == 'done'


def test_lock_rejects_second_holder():
    activity = _Activity(2)
    seen = {}

    def hold():
        seen['inner'] = _Activity(2).locked_work()

    assert activity.locked_work(hold=hold) == 'done'
    assert seen['inner'] == 'busy'


def test_lock_released_when_work_raises():
    activity = _Activity(3)
    with pytest.raises(RuntimeError):
        activity.failing_work()
    assert redisConn.get("lock:activity:3") is None


def test_lock_not_released_when_owned_by_someone_else():
    """持有者执行超时、锁被别人拿走后，原持有者收尾时不能把别人的锁删掉。"""
    activity = _Activity(4)

    def steal_lock():
        redisConn.set("lock:activity:4", 'other-owner')

    activity.locked_work(hold=steal_lock)
    assert redisConn.get("lock:activity:4") == b'other-owner'


def test_cache_hits_second_time():
    activity = _Activity(5)
    assert activity.load() == [1, 2, 3]
    assert activity.load() == [1, 2, 3]
    assert activity.calls == 1


def test_cache_force_refresh_skips_cache():
    activity = _Activity(6)
    activity.load()
    activity.load(forceRefreshCache=True)
    assert activity.calls == 2


def test_cache_ignores_legacy_pickle_value():
    """升级前写入的 pickle 缓存不能被反序列化，按未命中重新计算。"""
    redisConn.set("cache:activity:7", pickle.dumps([9, 9]))
    activity = _Activity(7)
    assert activity.load() == [1, 2, 3]
    assert activity.calls == 1


def test_cache_skips_value_that_is_not_json():
    activity = _Activity(8)
    assert activity.load_unserializable() == {1, 2, 3}
    assert redisConn.get("cache:activity-bad:8") is None
