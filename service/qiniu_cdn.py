#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

import util.config
from model.user import UserModel
from util.const.match import MODEL_STATUS_YES
from util.img_util import rgb_to_sketch
from util.qiniu_cdn import Qiniu


class MyStorage(object):
    def __init__(self, passportId):
        self.passportId = passportId

    @staticmethod
    def getObjNames(passportId):
        # 获取真实头像照片cdn对象名，以及虚拟头像照片cdn对象名
        fmt = "obj_name_secret:%s:localObjName:%s"
        realSeed = fmt % (util.config.get("qiniu", "secret_key"), passportId)
        virtualSeed = fmt % (util.config.get("qiniu", "secret_key"), hashlib.md5("%d" % passportId).hexdigest())
        return hashlib.md5(realSeed).hexdigest(), hashlib.md5(virtualSeed).hexdigest()

    def upload(self, imgStreamData):
        realObjName, virtualObjName = self.getObjNames(self.passportId)
        # 上传真实照片
        filename = "%s/%s" % ('head_img', realObjName)
        q = Qiniu()
        q.upload_stream(filename, imgStreamData)
        # 上传虚拟照片
        filename = "%s/%s" % ('head_img', virtualObjName)
        q = Qiniu()
        q.upload_stream(filename, rgb_to_sketch(imgStreamData))
        # 修改db
        UserModel.updateByPassportId(passportId=self.passportId, has_head_img=MODEL_STATUS_YES)
