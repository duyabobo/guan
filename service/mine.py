#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.user import UserModel
from service import BaseService
from service.qiniu_cdn import MyStorage
from util.const.match import MODEL_SEX_UNKNOWN_INDEX, MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX, MODEL_STATUS_NO, \
    MODEL_STATUS_EMPTY
from util.const.mini_program import *
from util.const.qiniu_img import CDN_QINIU_BOY_HEAD_IMG, CDN_QINIU_GIRL_HEAD_IMG, CDN_QINIU_CAMERA_HEAD_IMG


class MainFuncObj(object):
    def __init__(self, id, index, url, name, bindFuncName, needLogin=True, openType="", desc=""):
        self.id = id
        self.index = index
        self.url = url
        self.name = name
        self.bindFuncName = bindFuncName  # 小程序的点击触发方法名
        self.needLogin = needLogin
        self.openType = openType
        self.desc = desc


class MineService(BaseService):

    def getHeadImg(self, passportId):
        user = UserModel.getByPassportId(passportId=passportId)
        if not user or user.has_head_img == MODEL_STATUS_EMPTY:  # 未定义
            return CDN_QINIU_CAMERA_HEAD_IMG
        elif user.has_head_img == MODEL_STATUS_NO:  # 系统头像
            sexIndex = user.sexIndex if user else MODEL_SEX_UNKNOWN_INDEX
            return {
                MODEL_SEX_MALE_INDEX: CDN_QINIU_BOY_HEAD_IMG,
                MODEL_SEX_FEMALE_INDEX: CDN_QINIU_GIRL_HEAD_IMG,
                MODEL_SEX_UNKNOWN_INDEX: CDN_QINIU_CAMERA_HEAD_IMG
            }.get(sexIndex, CDN_QINIU_CAMERA_HEAD_IMG)
        else:  # 自定义头像（虚拟）
            return MyStorage.getVirtualImgUrl(passportId, user.head_img_version)

    def getMainGroupList(self):
        return [
            [
                MainFuncObj(1, 0, MYINFORMATION_PAGE, "我的资料", "clickMine"),
                MainFuncObj(2, 1, MYREQUIREMENT_PAGE, "我的期望", "clickMine"),
                # MainFuncObj(3, 2, MYDATE_PAGE, "我的见面", "clickMine"),
            ],
            [
                MainFuncObj(4, 0, SUGGESTION_PAGE, "客服", "handleContact", needLogin=False, openType="contact"),
                MainFuncObj(5, 1, SHARE_PAGE, "分享", "onShareAppMessage", needLogin=False, openType="share", desc="近水楼台先得月"),
            ],
            [
                MainFuncObj(6, 0, SECRET_PAGE, "隐私条款", "clickMine", needLogin=False),
                MainFuncObj(7, 1, ABOUT_PAGE, "关于我们", "clickMine", needLogin=False),
            ]
        ]
