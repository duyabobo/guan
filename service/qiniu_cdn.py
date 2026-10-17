#! /usr/bin/env python
# -*- coding: utf-8 -*-
import util.config
from util.const.qiniu_img import CDN_QINIU_URL
from util.encode import md5_hex
from util.qiniu_cdn import Qiniu


HEAD_IMG_VERSION = 0


class MyStorage(object):
    def __init__(self, passportId):
        self.passportId = passportId

    @staticmethod
    def getVirtualImgUrl(passportId, head_img_version):
        realObjName, virtualObjName = MyStorage.getObjNames(passportId)
        return CDN_QINIU_URL + virtualObjName + '?head_img_version=%s' % str(head_img_version)

    @staticmethod
    def getRealImgUrl(passportId, head_img_version):
        realObjName, virtualObjName = MyStorage.getObjNames(passportId)
        return CDN_QINIU_URL + realObjName + '?head_img_version=%d' % head_img_version

    @staticmethod
    def getVirtualThumbnailsImgUrl(passportId, head_img_version):
        realObjName, virtualObjName = MyStorage.getObjNames(passportId)
        return CDN_QINIU_URL + virtualObjName + '?imageMogr2/thumbnail/200x&head_img_version=%s' % str(head_img_version)

    @staticmethod
    def getRealThumbnailsImgUrl(passportId, head_img_version):
        realObjName, virtualObjName = MyStorage.getObjNames(passportId)
        return CDN_QINIU_URL + realObjName + '?imageMogr2/thumbnail/200x&head_img_version=%d' % head_img_version

    @staticmethod
    def getObjNames(passportId):
        fmt = "obj_name_secret:%s:passport_id:%s:head_img_version:%d"
        realSeed = fmt % (util.config.get("qiniu", "secret_key"), passportId, HEAD_IMG_VERSION)
        virtualSeed = fmt % (util.config.get("qiniu", "secret_key"), md5_hex("%d" % passportId), HEAD_IMG_VERSION)
        return "%s/%s" % ('head_img', md5_hex(realSeed)), \
               "%s/%s" % ('head_img', md5_hex(virtualSeed))

    def upload(self, imgStreamData):
        from util.img_util import rgb_to_sketch
        realObjName, virtualObjName = self.getObjNames(self.passportId)
        # 上传真实照片
        q = Qiniu()
        q.upload_stream(realObjName, imgStreamData)
        # 上传虚拟照片
        q = Qiniu()
        q.upload_stream(virtualObjName, rgb_to_sketch(imgStreamData))
