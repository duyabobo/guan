#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import time

from tornado.concurrent import run_on_executor

from handler.basehandler import BaseHandler
from util.con_runner import ConcurrencyExecutor
from util.monitor import super_monitor


def sleepA(n):
    print 'in A'
    time.sleep(n)
    print 'end A'
    return 'A'


def sleepB(n):
    print 'in B'
    time.sleep(n)
    print 'end B'
    return 'B'


def sleepC(n):
    print 'in c'
    time.sleep(n)
    print 'end C'


def sleepD(n):
    print 'in D'
    time.sleep(n)
    print 'end D'
    return 'D'


class ExampleHandler(BaseHandler):
    # 这里的例子用来实验 run_on_executor 的作用
    # 值得注意的是，如果本地启动了服务之后，使用浏览器打开多个窗口，同时请求访问这个接口，效果确是串行的！
    # 通过服务器这边日志可以显示串行的接受到请求，也就是说这是因为浏览器的一种防止并发行为。
    # 可以在请求这个接口的时候，后面加上不同的请求参数，就可以看到异步非阻塞效果了！！
    __model__ = ''

    @super_monitor
    def get(self):
        """注释, 说明这个接口是干嘛的, 以及一些注意事项, 请求和返回结果不必说明, 会单独写到 DOC 文档中的。
        """
        # 第一步, 把传参接受过来, 赋值给本地变量
        # 第二步, 请求数据访问层(dal), 数据库操作结束后, 需要立刻调用 finish_db_operation 释放数据库连接
        # 第三步, 调用 response 或者 redirect
        # 第四步, return response
        # 说明: 接口中不需要有日志抓取操作, 数据库操作要求: 一个接口只有一个 commit, 数据库操作层只需要执行 flush
        response = {'msg': 'abc', 'icp': '京ICP备20005743号-1'}
        return self.response(response)
