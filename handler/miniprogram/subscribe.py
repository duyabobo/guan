#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import gen

from handler.basehandler import BaseHandler
from service.subscribe import SubscribeService
from util.const.mini_program import SUBSCRIBE_ACTIVITY_START_NOTI_TID
from util.monitor import superMonitor, Response, superGenMonitor


class SubscribeCBHandler(BaseHandler):
    @superMonitor
    def post(self, *args, **kwargs):  # todo 用户订阅消息的操作处理回调，用以记录用户对订阅消息的操作类型和操作结果
        openid = self.getRequestParameter('openid')  # openid 是给用户发微信服务消息推送用的，要存储到缓存中，并且设置一个过期时间。因为我们数据库是不存储用户的openid的。
        guanId = self.getRequestParameter('guanId')
        subscribeRes = self.getRequestParameter('subscribeRes')
        return Response()


class SendMsgHandler(BaseHandler):

    @superGenMonitor
    @gen.coroutine
    def get(self):
        openid = self.getRequestParameter('openid', '')
        templateId = self.getRequestParameter('templateId', SUBSCRIBE_ACTIVITY_START_NOTI_TID)
        miniprogramState = self.getRequestParameter('miniprogramState', 'trial')  # formal/developer/trial
        ss = SubscribeService(openid, templateId, miniprogramState)
        yield ss.sendActivityStartMsg()
        raise gen.Return(Response())
