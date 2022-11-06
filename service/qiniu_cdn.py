#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

from model.user import UserModel
from util import str_util
from util.qiniu_cdn import Qiniu


class MyStorage(object):
    def __init__(self, passportId):
        self.passportId = passportId

    @staticmethod
    def getQiNiuObjName(passportId, local_obj_name):
        return hashlib.md5("passportId:%s:local_obj_name:%s" % (passportId, local_obj_name)).hexdigest()

    @property
    def objName(self):
        local_obj_name = str_util.getRandomStr()
        UserModel.updateByPassportId(passportId=self.passportId, head_img_obj_name=local_obj_name)
        return self.getQiNiuObjName(self.passportId, local_obj_name)

    def upload(self, imgStreamData):
        filename = "%s/%s" % ('head_img', self.objName)
        q = Qiniu()
        q.upload_stream(filename, imgStreamData)
        return filename
