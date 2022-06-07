#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.subscribe import SubscribeService
from util.const.mini_program import SUBSCRIBE_ACTIVITY_START_NOTI_TID
from util.monitor import superMonitor


class SubscribeCBHandler(BaseHandler):
    @superMonitor
    def post(self, *args, **kwargs):  # todo 用户订阅消息的操作处理回调，用以记录用户对订阅消息的操作类型和操作结果
        pass


class SendMsgHandler(BaseHandler):

    @superMonitor
    def get(self):
        openId = self.getRequestParameter('openid', '')
        templateId = self.getRequestParameter('templateId', SUBSCRIBE_ACTIVITY_START_NOTI_TID)
        miniprogramState = self.getRequestParameter('miniprogramState', 'trial')  # formal/developer/trial
        ss = SubscribeService(self.dbSession, self.redis, openId, templateId, miniprogramState)
        ret = ss.sendActivityStartMsg()
        return self.response(respData=ret)
