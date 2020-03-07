#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from models import GuanInfo


def get_guan_infoes(db_session, guan_id):
    """
    获取一个 guan_id 对应的问答数据
    :param db_session:
    :param guan_id:
    :return:
    """
    return db_session.query(GuanInfo).\
        filter(GuanInfo.guan_id == guan_id).\
        group_by(GuanInfo.id).\
        all()
