#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.ctx import getDbSession


class RequirementChangeRecordModel(BaseModel):
    """期望变化流水记录"""
    __tablename__ = 'requirement_change_record'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer)  # passport_id
    change_column = Column(String)  # 修改的column名
    new_value = Column(String)  # 修改后的字段值
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def addRecords(cls, passportId, **updateParams):
        records = []
        for k, v in updateParams.items():
            records.append(cls(
                passport_id=passportId,
                change_column=k,
                new_value=v
            ))
        getDbSession().add_all(records)
        getDbSession().flush()
