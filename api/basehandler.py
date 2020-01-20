#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import json

import pika
# 这个并发库, python3 自带, python2 需要: pip install futures
from concurrent.futures import ThreadPoolExecutor
from redis import StrictRedis
from sqlalchemy.orm import sessionmaker
from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler

import util.config
from ral import user
from util.const import EXCHANGE_NAME
from util.const import MOBILE_SECRET
from util.const import RESP_OK
from util.encode import jwt_decode
from util.monitor import super_monitor


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.application = application
        self.redis = StrictRedis(util.config.get('redis', 'host'), util.config.get('redis', 'port'))
        self._access_token = None
        self._db_session = None
        self._current_user = None
        self._mq_connection = None
        self._mq_channel = None
        self.executor = ThreadPoolExecutor(1)
        super(BaseHandler, self).__init__(self.application, request, **kwargs)

    @property
    def db_session(self):
        """
        数据库链接在需要的时候才会初始化, 而且不会重复初始化
        :return:
        """
        if hasattr(self, '_db_session') and self._db_session:
            return self._db_session
        self._db_session = sessionmaker(bind=self.application.engine)()
        return self._db_session

    @property
    def mq_connection(self):
        """
        rabbitmq 链接，在需要的时候初始化
        :return:
        """
        if hasattr(self, '_mq_connection') and self._mq_connection:
            return self._mq_connection
        mq_host = util.config.get('rabbitmq', 'host')
        self._mq_connection = pika.BlockingConnection(pika.ConnectionParameters(mq_host))
        return self._mq_connection

    @property
    def mq_channel(self):
        """
        rabbitmq 频道，在需要的时候初始化
        :return:
        """
        if hasattr(self, '_mq_channel') and self._mq_channel:
            return self._mq_channel
        self._mq_channel = self.mq_connection.channel()
        return self._mq_channel

    @property
    def access_token(self):
        """
        access_token 获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :return:
        """
        if hasattr(self, '_access_token') and self._access_token:
            return self._access_token
        self._access_token = self.get_request_parameter('access_token', None)
        return self._access_token

    @property
    def current_user(self):
        """
        获取当前登录用户的信息
        :return:
        """
        if hasattr(self, '_current_user') and self._current_user:
            return self._current_user
        self._current_user = user.get_current_user_info(self.redis, self.access_token)
        _mobile = self._current_user.get('mobile', '')
        if _mobile:
            self._current_user['mobile'] = jwt_decode(_mobile, MOBILE_SECRET).get('mobile', '')
        return self._current_user

    def put_offline_job_to_rabbitmq(self, routing_key, body_json):
        """
        抛出异步离线任务
        :param routing_key:
        :param body_json:
        :return:
        """
        return self.mq_channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(body_json),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

    def get_request_parameter(self, para_name, default=None, para_type=str):
        """
        获取请求体中的参数，获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :param para_name:
        :param default:
        :param para_type:
        :return:
        """
        def __get_parameter_from_body():
            if self.request.headers.get("Content-Type") == 'application/json' and self.request.body:
                return json.loads(self.request.body).get(para_name)
        request_parameter = self.get_argument(para_name, default=default)
        if request_parameter is None:
            request_parameter = __get_parameter_from_body()
        try:
            return para_type(request_parameter)
        except:
            return default

    def response(self, resp_json=None, resp_normal=RESP_OK):
        self.finish_db_operation(resp_normal)
        if self._mq_connection:
            self._mq_connection.close()
        if not resp_json:
            resp_json = {}
        resp_json.update(resp_normal)
        resp = json.dumps(resp_json)
        self.write(resp)
        return resp

    def finish_db_operation(self, resp_normal):
        """
        关闭数据库链接, 这个调用需要用在每个dal层函数里面, 理论上访问完数据库后应该立刻调用此方法。
        此方法将做如下操作: commit + close
        :return:
        """
        if resp_normal['code'] == 0:
            self.db_session.commit()
        else:
            self.db_session.rollback()
        self.db_session.close()

    def data_received(self, chunk):
        return

    @run_on_executor
    @super_monitor
    def head(self, *args, **kwargs):
        return

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        return

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        return

    @run_on_executor
    @super_monitor
    def delete(self, *args, **kwargs):
        return

    @run_on_executor
    @super_monitor
    def patch(self, *args, **kwargs):
        return

    @run_on_executor
    @super_monitor
    def put(self, *args, **kwargs):
        return

    @run_on_executor
    @super_monitor
    def options(self, *args, **kwargs):
        return
