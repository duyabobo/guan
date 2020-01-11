#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import time

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from util.monitor import super_monitor


class ExampleHandler(BaseHandler):
    # 这里的例子用来实验 run_on_executor 的作用
    # 值得注意的是，如果本地启动了服务之后，使用浏览器打开多个窗口，同时请求访问这个接口，效果确是串行的！
    # 通过服务器这边日志可以显示串行的接受到请求，也就是说这是因为浏览器的一种防止并发行为。
    # 可以在请求这个接口的时候，后面加上不同的请求参数，就可以看到异步非阻塞效果了！！
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self):
        """注释, 说明这个接口是干嘛的, 以及一些注意事项, 请求和返回结果不必说明, 会单独写到 DOC 文档中的。
        """
        # 第一步, 把传参接受过来, 赋值给本地变量
        # 第二步, 请求数据访问层(dal), 数据库操作结束后, 需要立刻调用 finish_db_operation 释放数据库连接
        # 第三步, 调用 response 或者 redirect
        # 第四步, return response
        # 说明: 接口中不需要有日志抓取操作, 数据库操作要求: 一个接口只有一个 commit, 数据库操作层只需要执行 flush
        print time.time()
        para_name = self.get_request_parameter('para_name')  # 接受参数，如果必传就不给出默认值
        print para_name
        time.sleep(10)
        response = {'msg': 'abc'}
        self.response(response)
        return response
