#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service import BaseService
from model.user import UserModel
from util import const


class MineService(BaseService):

    def getHeadImg(self, passportId):
        user = UserModel.getByPassportId(self.dbSession, passportId)
        sexIndex = user.sexIndex if user else const.MODEL_SEX_UNKNOWN_INDEX
        return {
            const.MODEL_SEX_MALE_INDEX: const.CDN_QINIU_BOY_HEAD_IMG,
            const.MODEL_SEX_FEMALE_INDEX: const.CDN_QINIU_GIRL_HEAD_IMG,
            const.MODEL_SEX_UNKNOWN_INDEX: const.CDN_QINIU_UNKNOWN_HEAD_IMG
        }.get(sexIndex, const.CDN_QINIU_UNKNOWN_HEAD_IMG)

    def getMainGroupList(self):
        return [
            [
                {
                    "id": 1,
                    "index": 0,
                    "url": const.MYINFORMATION_PAGE,
                    "name": '我的资料',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                },
                {
                    "id": 2,
                    "index": 1,
                    "url": const.MYREQUIREMENT_PAGE,
                    "name": '择偶条件',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                }
            ],
            [
                {
                    "id": 3,
                    "index": 0,
                    "url": const.SUGGESTION_PAGE,
                    "name": '客服',
                    "needLogin": False,
                    "openType": 'contact',
                    "bindFuncName": 'handleContact'
                },
                {
                    "id": 4,
                    "index": 1,
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
                    "index": 0,
                    "url": const.SECRET_PAGE,
                    "name": '隐私条款',
                    "needLogin": False,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                },
                {
                    "id": 6,
                    "index": 1,
                    "url": const.ABOUT_PAGE,
                    "name": '关于我们',
                    "needLogin": False,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                }
            ]
        ]
