#! /usr/bin/env python
# -*- coding: utf-8 -*-
import functools

import tornado.concurrent
from tornado import gen

from util.ctx import getManager


def timecost(deco_fn=None, step_name=None):
    # 放到@gen.coroutine装饰的方法上会无效
    def _timecost(fn):
        @functools.wraps(fn)
        def _wrap(*args, **kwargs):
            if step_name is None:
                _step_name = fn.__name__
            else:
                _step_name = step_name
            manager = getManager()
            manager.tc_child_in(_step_name)
            ret = fn(*args, **kwargs)
            if isinstance(ret, tornado.concurrent.Future):  # 这里会丢弃掉@gen.coroutine的方法
                manager.tc_child_drop()
            else:
                manager.tc_child_out()
            return ret
        return _wrap

    if deco_fn is not None and callable(deco_fn):
        return _timecost(deco_fn)
    return _timecost


def timecost_gen(deco_fn=None, step_name=None):
    # 要放到@gen.coroutine上面装饰
    def _timecost(fn):
        @functools.wraps(fn)
        @gen.coroutine
        def _wrap(*args, **kwargs):
            if step_name is None:
                _step_name = fn.__name__
            else:
                _step_name = step_name
            manager = getManager()
            manager.tc_child_in(_step_name)
            ret = yield fn(*args, **kwargs)
            manager.tc_child_out()
            raise gen.Return(ret)
        return _wrap

    if deco_fn is not None and callable(deco_fn):
        return _timecost(deco_fn)
    return _timecost
