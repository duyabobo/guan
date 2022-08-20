#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import functools
import json
import time

import pika
# 这个并发库, python3 自带, python2 需要: pip install futures
# from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import sessionmaker
# from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler

import util.config
from ral import passport
from util.const.base import EXCHANGE_NAME
from util.const.response import RESP_OK, RESP_SUCCESS_CODE, RESP_SUCCESS_WITH_NOTI_MIN_CODE
from util.ctx import LocalContext
from util.monitor import superMonitor, Response
from util.obj_util import object_2_dict


def packaging_response_data(fn):
    @functools.wraps(fn)
    def _wrap(wrap_self, *args, **kwargs):
        # 不管是否异步函数都统一用request_context封装
        wrap_self.dbSession.__enter__ = lambda: None
        wrap_self.dbSession.__exit__ = lambda type, value, traceback: None
        with LocalContext(lambda: wrap_self.dbSession):
            ret = fn(*args, **kwargs)
        return ret
    return _wrap


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.application = application
        self.timestamp = time.time()
        self._accessToken = ''
        self._sign = ''
        self._requestSeq = ''
        self._dbSession = None
        self._currentPassport = None
        self._mqConnection = None
        self._mqChannel = None
        super(BaseHandler, self).__init__(self.application, request, **kwargs)

    def __getattribute__(self, name):
        if name.upper() in BaseHandler.SUPPORTED_METHODS:
            method = packaging_response_data(super(BaseHandler, self).__getattribute__(name))
            setattr(self, name, method.__get__(self, self.__class__))
        return super(BaseHandler, self).__getattribute__(name)

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
        self._accessToken = self.getRequestParameter('accessToken', '')
        return self._accessToken

    @property
    def secret(self):
        return self.currentPassport.get('secret', 'secret')

    @property
    def sign(self):
        """
        header获取
        :return:
        """
        if hasattr(self, '_sign') and self._sign:
            return self._sign
        self._sign = self.request.headers.get('sign')
        return self._sign

    @property
    def requestSeq(self):
        """
        每次请求都有一个公共参数，请求序列号，后台可以依次防重放攻击
        """
        if hasattr(self, '_requestSeq') and self._requestSeq:
            return self._requestSeq
        self._requestSeq = self.getRequestParameter('requestSeq', '')
        return self._requestSeq

    @property
    def currentPassport(self):
        """
        获取当前登录用户的信息
        :return:
        """
        if hasattr(self, '_currentPassport') and self._currentPassport:
            return self._currentPassport
        self._currentPassport = passport.getSession(self.accessToken)
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

    def getRequestParameter(self, paraName, default='', paraType=str):
        """
        获取请求体中的参数，获取的优先顺序: url —— > body(x-www-form-urlencoded) ——> body(json)
        :param paraName:
        :param default:
        :param paraType:
        :return:
        """
        def __getParameterFromBody():
            if self.request.headers.get("Content-Type") == 'application/json' and self.request.body:
                return json.loads(self.request.body).get(paraName, default)
            return default
        requestParameter = self.get_argument(paraName, default=default)
        if not requestParameter:
            requestParameter = __getParameterFromBody()
        try:
            return paraType(requestParameter)
        except:
            return default

    def response(self, response):
        respData = response.data
        if not respData:
            respData = {}
        resp = {
            'data': object_2_dict(respData),
        }
        resp.update(response.msg)
        self.write(json.dumps(resp))
        self.finishDbOperation(response.msg)
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
