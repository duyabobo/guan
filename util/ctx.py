#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 利用tornado的 StackContext，构造一个线程全局变量栈。
# 主要解决每次请求都可以随时使用到同一个 dbSession 和 redisConn。
from tornado.stack_context import StackContext, _state

from util.database import mysql_offline_session


class LocalContext(StackContext):
    """继承自StackContext，StackContext基于线程号维护了状态对象即_state，_state里有一个内容栈。
    根据StackContext的 __enter__ 和 __exit__ 可以维护 _state里的内容栈。
    ：此处做出如下改动，以获取隐式随时获取 _state 里的内容栈信息。
    ：1，使用方式改变：with 语句放到每次handler的 get/post/put/delete方法最前面。见 BaseHandler 里处理过程。
        # with LocalContext(lamdba: dbSession):
        #   ret = fn(*args, **kwargs)
    ：2，功能改变：LocalContext增加一个类方法，可以直接返回（只查询非pop） _state 的内容栈。
    """

    @classmethod
    def current_data(cls):
        """
        :returns: current context
        """
        for ctx in reversed(_state.contexts[0]):
            if isinstance(ctx, cls) and ctx.active:
                return ctx.contexts[0]


def getDbSession():
    dbSession = LocalContext.current_data()
    if not dbSession:
        dbSession = mysql_offline_session
    return dbSession
