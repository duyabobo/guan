#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from sqlalchemy.sql import or_, and_

from model import BaseModel
from util.const import match
from util.ctx import getDbSession
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)


class NoticeSentModel(BaseModel):
    """到点提醒发出后记一笔，同一场同一人同一场景只发一次。"""
    __tablename__ = 'notice_sent'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, default=0)  # 不再写入真实场次编号
    slot_key = Column(String(64), default='')
    passport_id = Column(Integer, default=0)
    scene = Column(String(32), default='')
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def recent_passport_ids(cls, passport_ids, scene, since):
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not ids or not scene or not since:
            return set()
        rows = getDbSession().query(cls.passport_id).filter(
            cls.passport_id.in_(ids),
            cls.scene == scene,
            cls.status == match.MODEL_STATUS_YES,
            cls.create_time >= since,
        ).all()
        return {row.passport_id for row in rows}

    @classmethod
    def sent_keys_for(cls, activity_ids):
        ids = [activity_id for activity_id in activity_ids if activity_id]
        slot_of = _slot_of(ids)
        if not ids:
            return set()
        legacy = and_(cls.activity_id.in_(ids), cls.slot_key == '')
        linked = or_(cls.slot_key.in_(list(slot_of.keys())), legacy) if slot_of else legacy
        rows = getDbSession().query(cls.activity_id, cls.slot_key, cls.passport_id, cls.scene).filter(
            cls.status == match.MODEL_STATUS_YES,
            linked,
        ).all()
        return {_sent_key(row, slot_of) for row in rows if _sent_key(row, slot_of)}

    @classmethod
    def add_jobs(cls, jobs):
        if not jobs:
            return
        session = getDbSession()
        kept = 0
        for job in jobs:
            slot = activity_slot_key(job.activity_id)
            if not slot:
                logger.error("到点提醒未记，盲索引为空 activity=%s", job.activity_id)
                continue
            session.add(cls(
                activity_id=0,
                slot_key=slot,
                passport_id=job.passport_id,
                scene=job.scene,
                status=match.MODEL_STATUS_YES,
            ))
            kept += 1
        session.flush()
        logger.info("已记到点提醒 count=%s", kept)


def _slot_of(activity_ids):
    found = {}
    for activity_id in activity_ids:
        slot = activity_slot_key(activity_id)
        if slot:
            found[slot] = activity_id
    return found


def _sent_key(row, slot_of):
    activity_id = slot_of.get(row.slot_key) or (row.activity_id if not row.slot_key else 0)
    if not activity_id:
        return None
    return (activity_id, row.passport_id, row.scene)
