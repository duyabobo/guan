#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from models import GuanType


def get_guan_types(db_session):
    return db_session.query(GuanType).all()
