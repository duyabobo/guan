#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import functools
import json
import logging
import math
import time

from tornado.web import RequestHandler

from ral import passport
from util.database import SessionFactory
from util.const.response import RESP_SUCCESS_CODE, RESP_SUCCESS_WITH_NOTI_MIN_CODE
from util.ctx import LocalContext
from util.errors import InvalidParameter
from util.monitor import superMonitor
from util.obj_util import object_2_dict

logger = logging.getLogger(__name__)

JSON_CONTENT_TYPE = 'application/json'


def packaging_response_data(fn):
    @functools.wraps(fn)
    def _wrap(wrap_self, *args, **kwargs):
        # 不管是否异步函数都统一用request_context封装，后续在每次请求的任意地方，都可以通过 ctx.getManager 拿到 manager
        manager = Manager(wrap_self.dbSession)
        with LocalContext(lambda: manager):
            ret = fn(*args, **kwargs)
        return ret
    return _wrap


class Manager(object):
    def __init__(self, dbSession):
        self.dbSession = dbSession
        self.timecost_tree = self.create_new_child('root')
        self.child_filo = [self.timecost_tree]

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def get_cur_child(self):
        if not self.child_filo:
            return []
        return self.child_filo[-1]

    @staticmethod
    def create_new_child(step_name):
        return [step_name, 0, [], time.time() * 1000]  # [当前函数名，耗时，[子调用], 当前时间戳]

    def tc_child_in(self, step_name):
        cur_child = self.get_cur_child()
        new_child = self.create_new_child(step_name)
        cur_child[2].append(new_child)
        self.child_filo.append(new_child)

    def tc_child_out(self):
        cur_child = self.get_cur_child()
        if not cur_child:
            return
        cur_child[1] = time.time() * 1000 - cur_child[3]
        cur_child.pop()
        self.child_filo.pop()

    def tc_child_drop(self):
        # 放弃这个child
        self.child_filo[-2][2].pop()
        self.child_filo.pop()


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.application = application
        self.timestamp = time.time()
        self._accessToken = ''
        self._sign = ''
        self._requestSeq = ''
        self._dbSession = None
        self._currentPassport = None
        self._parsedJsonBody = None
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
        self._dbSession = SessionFactory()
        return self._dbSession

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

    def _jsonBody(self):
        """请求体按 JSON 解析一次并缓存。不是 JSON 对象时当作空字典，由参数校验去拒绝缺失的参数。"""
        if self._parsedJsonBody is not None:
            return self._parsedJsonBody
        parsed = {}
        content_type = (self.request.headers.get('Content-Type') or '').lower()
        if JSON_CONTENT_TYPE in content_type and self.request.body:
            try:
                loaded = json.loads(self.request.body)
            except ValueError:
                logger.info("请求体不是合法 JSON path=%s", self.request.path)
                loaded = None
            if isinstance(loaded, dict):
                parsed = loaded
        self._parsedJsonBody = parsed
        return parsed

    def _rawParameter(self, paraName):
        """取原始参数值，没有返回 None。顺序: url —— > body(x-www-form-urlencoded) ——> body(json)"""
        value = self.get_argument(paraName, default=None)
        if value:
            return value
        return self._jsonBody().get(paraName)

    def getRequestParameter(self, paraName, default='', paraType=str):
        """
        获取请求中的参数，缺失或转型失败都返回 default。必填或有取值范围的参数用 getIntParameter / getFloatParameter。
        :param paraName:
        :param default:
        :param paraType:
        :return:
        """
        raw = self._rawParameter(paraName)
        if raw is None:
            return default
        try:
            return paraType(raw)
        except (TypeError, ValueError):
            return default

    def getIntParameter(self, paraName, default=None, minimum=None, maximum=None, choices=None):
        """整数参数。default 为 None 表示必填。缺失、不是整数、越界、不在 choices 里都抛 InvalidParameter。"""
        raw = self._rawParameter(paraName)
        if raw is None or raw == '':
            return self._requiredOrDefault(paraName, default)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise InvalidParameter('%s 不是整数' % paraName)
        self._checkRange(paraName, value, minimum, maximum)
        if choices is not None and value not in choices:
            raise InvalidParameter('%s 不在允许的取值内' % paraName)
        return value

    def getFloatParameter(self, paraName, default=None, minimum=None, maximum=None):
        """浮点参数。default 为 None 表示必填。NaN、无穷大一律拒绝。"""
        raw = self._rawParameter(paraName)
        if raw is None or raw == '':
            return self._requiredOrDefault(paraName, default)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            raise InvalidParameter('%s 不是数字' % paraName)
        if not math.isfinite(value):
            raise InvalidParameter('%s 不是有限数字' % paraName)
        self._checkRange(paraName, value, minimum, maximum)
        return value

    @staticmethod
    def _requiredOrDefault(paraName, default):
        if default is None:
            raise InvalidParameter('缺少参数 %s' % paraName)
        return default

    @staticmethod
    def _checkRange(paraName, value, minimum, maximum):
        if minimum is not None and value < minimum:
            raise InvalidParameter('%s 小于下限 %s' % (paraName, minimum))
        if maximum is not None and value > maximum:
            raise InvalidParameter('%s 大于上限 %s' % (paraName, maximum))

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
