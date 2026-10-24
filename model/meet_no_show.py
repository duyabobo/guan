#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.ctx import getDbSession

logger = logging.getLogger(__name__)


class MeetNoShowModel(BaseModel):
    """已约上后又取消。同一场只记一次。"""
    __tablename__ = 'meet_no_show'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    activity_id = Column(Integer, default=0)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def count_of(cls, passport_id):
        if not passport_id:
            return 0
        return getDbSession().query(cls.id).filter(
            cls.passport_id == passport_id,
            cls.status == match.MODEL_STATUS_YES,
        ).count()

    @classmethod
    def add_once(cls, passport_id, activity_id):
        session = getDbSession()
        existing = session.query(cls).filter(
            cls.passport_id == passport_id,
            cls.activity_id == activity_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if existing:
            logger.info("爽约已记录 passport=%s activity=%s", passport_id, activity_id)
            return existing
        row = cls(
            passport_id=passport_id,
            activity_id=activity_id,
            status=match.MODEL_STATUS_YES,
        )
        session.add(row)
        session.flush()
        logger.info("已记录爽约 passport=%s activity=%s", passport_id, activity_id)
        return row
