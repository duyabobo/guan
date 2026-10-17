#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.ctx import getDbSession

logger = logging.getLogger(__name__)


class ProfileAttrModel(BaseModel):
    """个人资料与个人期望。一个用户、一个范围、一个维度对应一行。"""
    __tablename__ = 'profile_attr'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    scope = Column(String(16), default='')  # info / requirement
    dim_key = Column(String(64), default='')
    value_text = Column(String(512), default='')
    value_min = Column(Integer, default=0)  # 单值，或区间下限
    value_max = Column(Integer, default=0)  # 区间上限；单值为 0
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def listByPassportId(cls, passport_id):
        if not passport_id:
            return []
        return cls.listByPassportIds([passport_id])

    @classmethod
    def listByPassportIds(cls, passport_ids):
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not ids:
            return []
        return getDbSession().query(cls).filter(
            cls.passport_id.in_(ids),
            cls.status == match.MODEL_STATUS_YES,
        ).all()

    @classmethod
    def saveScope(cls, passport_id, scope, values_by_key):
        """按维度覆盖写入。先一次查出已有行，再在内存里改，避免循环里查库。"""
        if not passport_id or not values_by_key:
            return
        session = getDbSession()
        existing = session.query(cls).filter(
            cls.passport_id == passport_id,
            cls.scope == scope,
            cls.dim_key.in_(list(values_by_key.keys())),
        ).all()
        by_key = {row.dim_key: row for row in existing}
        for dim_key, value in values_by_key.items():
            _apply_value(session, by_key.get(dim_key), passport_id, scope, dim_key, value)
        session.commit()
        logger.info("profile_attr saved passport=%s scope=%s dims=%s",
                    passport_id, scope, list(values_by_key.keys()))


def _apply_value(session, row, passport_id, scope, dim_key, value):
    if row is None:
        session.add(ProfileAttrModel(
            passport_id=passport_id,
            scope=scope,
            dim_key=dim_key,
            value_min=value["value_min"],
            value_max=value["value_max"],
            value_text=value["value_text"],
            status=match.MODEL_STATUS_YES,
        ))
        return
    row.value_min = value["value_min"]
    row.value_max = value["value_max"]
    row.value_text = value["value_text"]
    row.status = match.MODEL_STATUS_YES
