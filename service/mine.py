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
