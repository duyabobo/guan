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
from util.const import RESP_OK
from util.monitor import superMonitor


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.application = application
        self.redis = StrictRedis(util.config.get('redis', 'host'), util.config.get('redis', 'port'))
        self._accessToken = None
        self._dbSession = None
        self._currentUser = None
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
    def currentUser(self):
        """
        获取当前登录用户的信息
        :return:
        """
        if hasattr(self, '_currentUser') and self._currentUser:
            return self._currentUser
        self._currentUser = passport.getCurrentUserInfo(self.redis, self.accessToken)
        self._currentUser['mobile'] = self._currentUser.get('mobile', '')
        return self._currentUser

    @property
    def currentUId(self):
        """
        获取当前用户id，如果未登录，就是0
        :return:
        """
        return self.currentUser.get('id', 0)

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

    def response(self, respJson=None, respNormal=RESP_OK):
        if not respJson:
            respJson = {}
        respJson.update(respNormal)
        resp = json.dumps(respJson)
        self.write(resp)
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
        if respNormal['code'] == 0:
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
