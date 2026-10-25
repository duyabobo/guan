#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""进程内定时扫描到点提醒。"""
import datetime
import logging

import tornado.ioloop
from sqlalchemy.orm import sessionmaker

from service.meet_notice import MeetNoticeService
from util.const.notice import NOTICE_SCAN_LOCK_KEY, SCAN_INTERVAL_MS, SCAN_LOCK_SEC
from util.ctx import LocalContext
from util.database import engine
from util.redis_conn import redisConn

logger = logging.getLogger(__name__)


class _DbHolder(object):
    def __init__(self, db_session):
        self.dbSession = db_session


def scan_due_notices():
    got = redisConn.set(NOTICE_SCAN_LOCK_KEY, 1, nx=True, ex=SCAN_LOCK_SEC)
    if not got:
        logger.info("见面提醒扫描跳过，上一轮还没结束")
        return
    try:
        _scan_in_session()
    finally:
        redisConn.delete(NOTICE_SCAN_LOCK_KEY)


def _scan_in_session():
    session = sessionmaker(bind=engine)()
    holder = _DbHolder(session)
    try:
        with LocalContext(lambda: holder):
            MeetNoticeService.scan(datetime.datetime.now())
        session.commit()
    finally:
        session.close()


def start_notice_scan(io_loop):
    io_loop.add_callback(scan_due_notices)
    tornado.ioloop.PeriodicCallback(scan_due_notices, SCAN_INTERVAL_MS).start()
    logger.info("见面提醒扫描已启动 interval_ms=%s", SCAN_INTERVAL_MS)
