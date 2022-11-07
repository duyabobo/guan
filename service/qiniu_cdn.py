#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

import util.config
from util.qiniu_cdn import Qiniu


class MyStorage(object):
    def __init__(self, passportId):
        self.passportId = passportId

    @property
    def objName(self):
        localObjName = hashlib.md5("%d" % self.passportId).hexdigest()
        return hashlib.md5("obj_name_secret:%s:localObjName:%s" % (util.config.get("qiniu", "secret_key"), localObjName)).hexdigest()

    def upload(self, imgStreamData):
        filename = "%s/%s" % ('head_img', self.objName)
        q = Qiniu()
        q.upload_stream(filename, imgStreamData)
        return filename
