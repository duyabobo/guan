#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import json

import pika
# 这个并发库, python3 自带, python2 需要: pip install futures
# from concurrent.futures import ThreadPoolExecutor
from redis import StrictRedis
from sqlalchemy.orm import sessionmaker
# from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler

import util.config
from ral import passport
from util.const import EXCHANGE_NAME
from util.const import RESP_OK, RESP_SUCCESS_CODE, RESP_SUCCESS_WITH_NOTI_MIN_CODE
from util.monitor import superMonitor


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.application = application
        self.redis = StrictRedis(util.config.get('redis', 'host'), util.config.get('redis', 'port'))
        self._accessToken = None
        self._sign = None
        self._timestamp = None
        self._dbSession = None
        self._currentPassport = None
        self._mqConnection = None
        self._mqChannel = None
        super(BaseHandler, self).__init__(self.application, request, **kwargs)

    @property
    def dbSession(self):
        """
        数据库链接在需要的时候才会初始化, 而且不会重复初始化
        :return:
        """
        if hasattr(self, '_dbSession') and self._dbSession:
            return self._dbSession
        self._dbSession = sessionmaker(bind=self.application.engine)()
        return self._dbSession

    @property
    def mqConnection(self):
        """
        rabbitmq 链接，在需要的时候初始化
        :return:
        """
        if hasattr(self, '_mqConnection') and self._mqConnection:
            return self._mqConnection
        mq_host = util.config.get('rabbitmq', 'host')
        self._mqConnection = pika.BlockingConnection(pika.ConnectionParameters(mq_host))
        return self._mqConnection

    @property
    def mqChannel(self):
        """
        rabbitmq 频道，在需要的时候初始化
        :return:
        """
        if hasattr(self, '_mqChannel') and self._mqChannel:
            return self._mqChannel
        self._mqChannel = self.mqConnection.channel()
        return self._mqChannel

    @property
    def accessToken(self):
        """
        accessToken 获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :return:
        """
        if hasattr(self, '_accessToken') and self._accessToken:
            return self._accessToken
        self._accessToken = self.getRequestParameter('accessToken', None)
        return self._accessToken

    @property
    def sign(self):
        """
        获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :return:
        """
        if hasattr(self, '_sign') and self._sign:
            return self._sign
        self._sign = self.getRequestParameter('sign', None)
        return self._sign

    @property
    def timestamp(self):
        """
        获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :return:
        """
        if hasattr(self, '_timestamp') and self._timestamp:
            return self._timestamp
        self._timestamp = self.getRequestParameter('timestamp', None)
        return self._timestamp

    @property
    def currentPassport(self):
        """
        获取当前登录用户的信息
        :return:
        """
        if hasattr(self, '_currentPassport') and self._currentPassport:
            return self._currentPassport
        self._currentPassport = passport.getSession(self.redis, self.accessToken)
        self._currentPassport['id'] = int(self._currentPassport.get('id', 0))  # redis取出来都是str，这里转一下
        return self._currentPassport

    @property
    def currentPassportId(self):
        """
        获取当前用户id，如果未登录，就是0
        :return:
        """
        return self.currentPassport.get('id', 0)

    def putOfflineJobToRabbitmq(self, routingKey, bodyJson):
        """
        抛出异步离线任务
        :param routingKey:
        :param bodyJson:
        :return:
        """
        return self.mqChannel.basic_publish(
            exchange=EXCHANGE_NAME,
            routingKey=routingKey,
            body=json.dumps(bodyJson),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

    def getRequestParameter(self, paraName, default=None, paraType=str):
        """
        获取请求体中的参数，获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :param paraName:
        :param default:
        :param paraType:
        :return:
        """
        def __getParameterFromBody():
            if self.request.headers.get("Content-Type") == 'application/json' and self.request.body:
                return json.loads(self.request.body).get(paraName)
        requestParameter = self.get_argument(paraName, default=default)
        if requestParameter is None:
            requestParameter = __getParameterFromBody()
        try:
            return paraType(requestParameter)
        except:
            return default

    def response(self, respData=None, respNormal=RESP_OK):
        if not respData:
            respData = {}
        resp = {
            'data': respData,
        }
        resp.update(respNormal)
        self.write(json.dumps(resp))
        self.finishDbOperation(respNormal)
        if self._mqConnection:
            self._mqConnection.close()
        return resp

    def finishDbOperation(self, respNormal):
        """
        关闭数据库链接, 这个调用需要用在每个dal层函数里面, 理论上访问完数据库后应该立刻调用此方法。
        此方法将做如下操作: commit + close
        :return:
        """
        if respNormal['code'] == RESP_SUCCESS_CODE or respNormal['code'] > RESP_SUCCESS_WITH_NOTI_MIN_CODE:
            self.dbSession.commit()
        else:
            self.dbSession.rollback()
        self.dbSession.close()

    def data_received(self, chunk):
        return

    @superMonitor
    def head(self, *args, **kwargs):
        return

    @superMonitor
    def get(self, *args, **kwargs):
        return

    @superMonitor
    def post(self, *args, **kwargs):
        return

    @superMonitor
    def delete(self, *args, **kwargs):
        return

    @superMonitor
    def patch(self, *args, **kwargs):
        return

    @superMonitor
    def put(self, *args, **kwargs):
        return

    @superMonitor
    def options(self, *args, **kwargs):
        return
