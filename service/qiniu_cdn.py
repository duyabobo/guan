#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

from model.user import UserModel
from util.qiniu_cdn import Qiniu


class MyStorage(object):
    def __init__(self, passportId):
        self.passportId = passportId

    @staticmethod
    def getQiNiuObjName(passportId, localObjName):
        return hashlib.md5("passportId:%s:localObjName:%s" % (passportId, localObjName)).hexdigest()

    @property
    def objName(self):
        localObjName = hashlib.md5("%d" % self.passportId).hexdigest()
        UserModel.updateByPassportId(passportId=self.passportId, head_img_obj_name=localObjName)
        return self.getQiNiuObjName(self.passportId, localObjName)

    def upload(self, imgStreamData):
        filename = "%s/%s" % ('head_img', self.objName)
        q = Qiniu()
        q.upload_stream(filename, imgStreamData)
        return filename
