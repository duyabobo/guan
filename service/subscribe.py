#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util import const
from util.wx_mini import WxHelper


class SubscribeService(object):

    def __init__(self, openId, templateId, miniprogram_state):
        self.openId = openId
        self.templateId = templateId
        self.miniprogramState = miniprogram_state

    def sendActivityStartMsg(self):
        page = const.GUANINFO_SHORT_PAGE.format(guan_id=1)  # todo guan_id 需要查询
        data = {
          "thing1": {
              "value": "您参加的相亲活动即将开始，请准时参加。"
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
        return WxHelper().sendSubscribeMsg(self.openId, self.templateId, page, data, self.miniprogramState)
