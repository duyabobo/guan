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


class NoticeSentModel(BaseModel):
    """到点提醒发出后记一笔，同一场同一人同一场景只发一次。"""
    __tablename__ = 'notice_sent'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, default=0)
    passport_id = Column(Integer, default=0)
    scene = Column(String(32), default='')
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def sent_keys_for(cls, activity_ids):
        ids = [activity_id for activity_id in activity_ids if activity_id]
        if not ids:
            return set()
        rows = getDbSession().query(cls.activity_id, cls.passport_id, cls.scene).filter(
            cls.activity_id.in_(ids),
            cls.status == match.MODEL_STATUS_YES,
        ).all()
        return {(row.activity_id, row.passport_id, row.scene) for row in rows}

    @classmethod
    def add_jobs(cls, jobs):
        if not jobs:
            return
        session = getDbSession()
        for job in jobs:
            session.add(cls(
                activity_id=job.activity_id,
                passport_id=job.passport_id,
                scene=job.scene,
                status=match.MODEL_STATUS_YES,
            ))
        session.flush()
        logger.info("已记到点提醒 count=%s", len(jobs))
