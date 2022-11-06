#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.common.selector import VALUE_TYPE_DICT
from service.myself import UserInfoService
from util.monitor import superMonitor, Response


class MyselfHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        uis = UserInfoService(self.currentPassport)
        return Response(data=uis.getMyselfInfo())

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType')
        column = self.getRequestParameter('column', paraType=int)
        valueType = VALUE_TYPE_DICT[opType]
        value = self.getRequestParameter('value', paraType=valueType)

        uis = UserInfoService(self.currentPassport)
        ret = uis.checkBeforeUpdate(opType, value)
        if ret:
            return Response(msg=ret)
        return Response(data=uis.updateMyselfInfo(opType, value, column=column))


class HeadImgHandler(BaseHandler):
    def post(self, *args, **kwargs):  # 上传+更新头像
        pass

    def put(self, *args, **kwargs):  # 使用默认头像
        uis = UserInfoService(self.currentPassport)
        uis.resetHeadImg()
        return Response()
