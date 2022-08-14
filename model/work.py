#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP

from model import BaseModel
from ral.cache import checkInconsistentCache
from util.const.base import EMPTY_STR
from util.const.match import MODEL_STATUS_YES
from util.ctx import getDbSession


class WorkModel(BaseModel):
    """工作信息"""
    __tablename__ = 'work'
    id = Column(Integer, primary_key=True)  # id
    profession = Column(String, default=EMPTY_STR)  # 行业
    industry = Column(String, default=EMPTY_STR)  # 方向
    position = Column(String, default=EMPTY_STR)  # 职位
    seq = Column(Integer, default=0)  # 序号越小越靠前。10位从高到低分配规则：1～5位支持42948个学校，6-7位支持99种学历类型，8-10位支持1000个专业
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getById(cls, workId):
        return getDbSession().query(cls).filter(cls.id == workId, cls.status == MODEL_STATUS_YES).first()


