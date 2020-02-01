#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/1'
from models import Suggestion


def add_suggestion(db_session, user_id, suggestion_content):
    """
    增加一个意见记录
    :param db_session:
    :param user_id:
    :param suggestion_content:
    :return:
    """
    suggestion = Suggestion(
        user_id=user_id,
        suggestion_content=suggestion_content
    )
    db_session.add(suggestion)
    db_session.flush()
    return suggestion
