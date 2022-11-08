#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

import util.config
from model.user import UserModel
from util.const.match import MODEL_STATUS_YES
from util.const.qiniu_img import CDN_QINIU_URL
from util.img_util import rgb_to_sketch
from util.qiniu_cdn import Qiniu


class MyStorage(object):
    def __init__(self, passportId):
        self.passportId = passportId

    @staticmethod
    def getVirtualImgUrl(passportId):
        realObjName, virtualObjName = MyStorage.getObjNames(passportId)
        return CDN_QINIU_URL + virtualObjName

    @staticmethod
    def getRealImgUrl(passportId):
        realObjName, virtualObjName = MyStorage.getObjNames(passportId)
        return CDN_QINIU_URL + realObjName

    @staticmethod
    def getObjNames(passportId):
        # 获取真实头像照片cdn对象名，以及虚拟头像照片cdn对象名
        fmt = "obj_name_secret:%s:localObjName:%s"
        realSeed = fmt % (util.config.get("qiniu", "secret_key"), passportId)
        virtualSeed = fmt % (util.config.get("qiniu", "secret_key"), hashlib.md5("%d" % passportId).hexdigest())
        return "%s/%s" % ('head_img', hashlib.md5(realSeed).hexdigest()), \
               "%s/%s" % ('head_img', hashlib.md5(virtualSeed).hexdigest())

    def upload(self, imgStreamData):
        realObjName, virtualObjName = self.getObjNames(self.passportId)
        # 上传真实照片
        q = Qiniu()
        q.upload_stream(realObjName, imgStreamData)
        # 上传虚拟照片
        q = Qiniu()
        q.upload_stream(virtualObjName, rgb_to_sketch(imgStreamData))
        # 修改db
        UserModel.updateByPassportId(passportId=self.passportId, has_head_img=MODEL_STATUS_YES)
