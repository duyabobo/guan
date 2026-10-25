#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 利用 Python 3.7+ contextvars 构造请求级别的上下文变量
# tornado.stack_context 在 Tornado 6.0 中已被移除，此处用 contextvars 替代，接口保持兼容。

from contextvars import ContextVar


# 每个请求的协程/线程拥有独立的 manager 上下文
_manager_ctx: ContextVar = ContextVar('manager', default=None)


class LocalContext:
    """模拟原 StackContext 的 with 语句接口，基于 contextvars 实现协程安全的请求上下文。

    用法（与原 StackContext 完全兼容）：
        with LocalContext(lambda: manager):
            ret = fn(*args, **kwargs)
    """

    def __init__(self, context_factory):
        self._context_factory = context_factory
        self._token = None

    def __enter__(self):
        self._token = _manager_ctx.set(self._context_factory())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token is not None:
            _manager_ctx.reset(self._token)


def getManager():
    return _manager_ctx.get()


def getDbSession():
    """当前请求（或后台任务）的 Session。没有上下文就是用法错误，不能悄悄退回一个全局共享的 Session。"""
    manager = getManager()
    if not manager:
        raise RuntimeError('没有请求上下文：先用 LocalContext 包住，再访问数据库')
    return manager.dbSession
