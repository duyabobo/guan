#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import gen

from service import BaseService
from util.const.mini_program import GUANINFO_SHORT_PAGE
from util.wx_mini import WxHelper


class SubscribeService(BaseService):

    def __init__(self, openid, templateId, miniprogram_state):
        self.openid = openid
        self.templateId = templateId
        self.miniprogramState = miniprogram_state
        super(SubscribeService, self).__init__()

    @gen.coroutine
    def sendActivityStartMsg(self):
        page = GUANINFO_SHORT_PAGE.format(guan_id=1)  # todo guan_id 需要查询
        data = {
          "thing1": {
              "value": "您参加的见面活动即将开始，请准时参加。"
          },
          "thing2": {
              "value": "五道口"  # todo 计算用户参与活动的地点
          },
          "date3": {
              "value": "2022-02-22 12:00"
          },
          "date4": {
              "value": "2022-02-22 14:00"
          }
        }
        yield WxHelper().sendSubscribeMsg(self.openid, self.templateId, page, data, self.miniprogramState)
        return
