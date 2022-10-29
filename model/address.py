#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.const.base import EMPTY_STR
from util.const.qiniu_img import CDN_QINIU_ADDRESS_URL
from util.ctx import getDbSession


class AddressModel(BaseModel):
    """地点"""
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # name，这里要注意和img名保持一致，拼音转换后就是图片对象的名
    description = Column(String, default=EMPTY_STR)  # 地点描述(人均消费/吃喝玩乐推荐)
    region_id = Column(Integer, default=0)  # 省市区id
    longitude = Column(Float, default=0)  # 经度
    latitude = Column(Float, default=0)  # 纬度
    img_obj_name = Column(String, default="")  # oss的对象名，比如七牛
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @property
    def img(self):  # 图片url
        return "{qiniuUrl}{objName}".format(qiniuUrl=CDN_QINIU_ADDRESS_URL, objName=self.img_obj_name)

    @property
    def thumbnails_img(self):  # 缩略图url
        return "{qiniuUrl}{objName}?imageMogr2/thumbnail/188x".format(qiniuUrl=CDN_QINIU_ADDRESS_URL, objName=self.img_obj_name)

    @classmethod
    def listByLongitudeLatitude(cls, longitude, latitude):  # todo
        return getDbSession().query(cls).filter(cls.status == match.MODEL_STATUS_YES).all()

    @classmethod
    def getById(cls, addressId):
        return getDbSession().query(cls).filter(cls.id == addressId, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def listByIds(cls, addressIds):
        if not addressIds:
            return []
        return getDbSession().query(cls).filter(cls.id.in_(addressIds), cls.status == match.MODEL_STATUS_YES)

    @classmethod
    def getAddressList(cls):
        return getDbSession().query(cls).filter(cls.status == match.MODEL_STATUS_YES)

    @property
    def nameShort(self):
        if len(self.name) <= 15:
            return self.name
        else:
            return self.name[:15] + "..."

    @property
    def nameLong(self):
        if len(self.name) <= 22:
            return self.name
        else:
            return self.name[:22] + "..."
