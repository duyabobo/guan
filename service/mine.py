#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.user import UserModel
from service import BaseService
from util.const.mini_program import *
from util.const.model import MODEL_SEX_UNKNOWN_INDEX, MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX
from util.const.qiniu_img import CDN_QINIU_BOY_HEAD_IMG, CDN_QINIU_GIRL_HEAD_IMG, CDN_QINIU_UNKNOWN_HEAD_IMG


class MineService(BaseService):

    def getHeadImg(self, passportId):
        user = UserModel.getByPassportId(self.dbSession, passportId)
        sexIndex = user.sexIndex if user else MODEL_SEX_UNKNOWN_INDEX
        return {
            MODEL_SEX_MALE_INDEX: CDN_QINIU_BOY_HEAD_IMG,
            MODEL_SEX_FEMALE_INDEX: CDN_QINIU_GIRL_HEAD_IMG,
            MODEL_SEX_UNKNOWN_INDEX: CDN_QINIU_UNKNOWN_HEAD_IMG
        }.get(sexIndex, CDN_QINIU_UNKNOWN_HEAD_IMG)

    def getMainGroupList(self):
        return [
            [
                {
                    "id": 1,
                    "index": 0,
                    "url": MYINFORMATION_PAGE,
                    "name": '我的资料',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                },
                {
                    "id": 2,
                    "index": 1,
                    "url": MYREQUIREMENT_PAGE,
                    "name": '见面条件',
                    "needLogin": True,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                }
            ],
            [
                {
                    "id": 3,
                    "index": 0,
                    "url": SUGGESTION_PAGE,
                    "name": '客服',
                    "needLogin": False,
                    "openType": 'contact',
                    "bindFuncName": 'handleContact'
                },
                {
                    "id": 4,
                    "index": 1,
                    "url": SHARE_PAGE,
                    "name": '分享',
                    "desc": '近水楼台先得月',
                    "needLogin": False,
                    "openType": 'share',
                    "bindFuncName": 'onShareAppMessage'
                }
            ],
            [
                {
                    "id": 5,
                    "index": 0,
                    "url": SECRET_PAGE,
                    "name": '隐私条款',
                    "needLogin": False,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                },
                {
                    "id": 6,
                    "index": 1,
                    "url": ABOUT_PAGE,
                    "name": '关于我们',
                    "needLogin": False,
                    "openType": '',
                    "bindFuncName": 'clickMine'
                }
            ]
        ]
