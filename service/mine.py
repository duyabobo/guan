#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service import BaseService
from model.user import UserModel
from util import const


class MineService(BaseService):

    def getHeadImg(self, passportId):
        user = UserModel.getByPassportId(self.dbSession, passportId)
        sex = user.sex if user else const.MODEL_SEX_UNKNOWN
        return {
            const.MODEL_SEX_MALE: const.CDN_QINIU_BOY_HEAD_IMG,
            const.MODEL_SEX_FEMALE: const.CDN_QINIU_GIRL_HEAD_IMG,
            const.MODEL_SEX_UNKNOWN: const.CDN_QINIU_UNKNOWN_HEAD_IMG
        }.get(sex, const.CDN_QINIU_UNKNOWN_HEAD_IMG)

    def getMainGroupList(self):
        return [
            [
                {
                    "id": 1,
                    "url": const.MYINFORMATION_PAGE,
                    "name": '我的资料',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                },
                {
                    "id": 2,
                    "url": const.MYREQUIREMENT_PAGE,
                    "name": '我的期望',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                }
            ],
            [
                {
                    "id": 3,
                    "url": const.SUGGESTION_PAGE,
                    "name": '客服',
                    "needLogin": False,
                    "openType": 'contact',
                    "bindFuncName": 'handleContact'
                },
                {
                    "id": 4,
                    "url": const.SHARE_PAGE,
                    "name": '分享',
                    "needLogin": False,
                    "openType": 'share',
                    "bindFuncName": 'onShareAppMessage'
                }
            ],
            [
                {
                    "id": 5,
                    "url": const.SETTING_PAGE,
                    "name": '设置',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                },
                {
                    "id": 6,
                    "url": const.ABOUT_PAGE,
                    "name": '关于',
                    "needLogin": False,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                }
            ]
        ]
