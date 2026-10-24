#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用 profile_attr 判断一个人的资料是否满足另一人的期望。

期望侧没填的维度当作不限。比较规则写在维度目录的 match_rule 上，
新增维度不用改这里。
"""
import logging

from service.common.profile_catalog import (
    ACTIVE_DIMS,
    MATCH_RULE_EXACT,
    MATCH_RULE_RANGE,
    MATCH_RULE_TEXT,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
)
from util.const.base import ALL_STR

logger = logging.getLogger(__name__)


def requirement_accepts(info_map, requirement_map):
    """info_map / requirement_map: dim_key -> 属性行。"""
    requirement_map = requirement_map or {}
    info_map = info_map or {}
    for dim in ACTIVE_DIMS:
        if not _dim_accepts(dim, info_map.get(dim.key), requirement_map.get(dim.key)):
            return False
    return True


def rows_to_scope_map(rows, scope):
    return {row.dim_key: row for row in rows or [] if row.scope == scope}


def inviter_passport_id(activity):
    """邀请中的活动只有一方入座，期望以这一方为准。空场或双方都在则没有单一邀请人。"""
    boy_id = activity.boy_passport_id or 0
    girl_id = activity.girl_passport_id or 0
    if boy_id and not girl_id:
        return boy_id
    if girl_id and not boy_id:
        return girl_id
    return 0


def other_passport_id(activity, passport_id):
    """座位上的另一个人。没有对方时是 0。"""
    boy_id = activity.boy_passport_id or 0
    girl_id = activity.girl_passport_id or 0
    if passport_id == boy_id:
        return girl_id
    if passport_id == girl_id:
        return boy_id
    return 0


def seated_passport_ids(activity):
    ids = []
    for passport_id in (activity.boy_passport_id or 0, activity.girl_passport_id or 0):
        if passport_id:
            ids.append(passport_id)
    return ids


class ProfileMatchService(object):

    @staticmethod
    def user_accepts_requirement(user_passport_id, requirement_passport_id):
        from model.profile_attr import ProfileAttrModel
        rows = ProfileAttrModel.listByPassportIds([user_passport_id, requirement_passport_id])
        info_map = rows_to_scope_map(
            [row for row in rows if row.passport_id == user_passport_id], SCOPE_INFO)
        requirement_map = rows_to_scope_map(
            [row for row in rows if row.passport_id == requirement_passport_id], SCOPE_REQUIREMENT)
        accepted = requirement_accepts(info_map, requirement_map)
        logger.info(
            "profile match user=%s requirement_owner=%s accepted=%s",
            user_passport_id, requirement_passport_id, accepted,
        )
        return accepted

    @staticmethod
    def matched_activity_ids(passport_id, activities):
        """空场算匹配。邀请中的场次，用邀请人的期望对当前用户的资料做一次批量比较。"""
        activities = list(activities or [])
        inviting = []
        matched = set()
        for activity in activities:
            inviter_id = inviter_passport_id(activity)
            if not inviter_id:
                matched.add(activity.id)
                continue
            inviting.append((activity.id, inviter_id))

        if not inviting:
            logger.info("profile match list passport=%s empty=%s", passport_id, len(matched))
            return matched

        from model.profile_attr import ProfileAttrModel
        passport_ids = [passport_id] + [inviter_id for _, inviter_id in inviting]
        rows = ProfileAttrModel.listByPassportIds(passport_ids)
        info_map = rows_to_scope_map(
            [row for row in rows if row.passport_id == passport_id], SCOPE_INFO)
        requirement_by_owner = _requirement_maps(rows, passport_id)
        for activity_id, inviter_id in inviting:
            if requirement_accepts(info_map, requirement_by_owner.get(inviter_id, {})):
                matched.add(activity_id)
        logger.info(
            "profile match list passport=%s candidates=%s matched=%s",
            passport_id, len(activities), len(matched),
        )
        return matched


def _requirement_maps(rows, viewer_passport_id):
    grouped = {}
    for row in rows:
        if row.passport_id == viewer_passport_id or row.scope != SCOPE_REQUIREMENT:
            continue
        grouped.setdefault(row.passport_id, {})[row.dim_key] = row
    return grouped


def _dim_accepts(dim, info_row, requirement_row):
    if dim.match_rule == MATCH_RULE_RANGE:
        return _range_accepts(info_row, requirement_row)
    if dim.match_rule == MATCH_RULE_TEXT:
        return _text_accepts(info_row, requirement_row)
    if dim.match_rule == MATCH_RULE_EXACT:
        return _exact_accepts(info_row, requirement_row)
    logger.warning("unknown match rule dim=%s rule=%s", dim.key, dim.match_rule)
    return True


def _range_accepts(info_row, requirement_row):
    if requirement_row is None:
        return True
    low = requirement_row.value_min or 0
    high = requirement_row.value_max or 0
    if not low and not high:
        return True
    value = info_row.value_min if info_row else 0
    if not value:
        return False
    if low and value < low:
        return False
    if high and value > high:
        return False
    return True


def _exact_accepts(info_row, requirement_row):
    if requirement_row is None or not requirement_row.value_min:
        return True
    if info_row is None:
        return False
    return info_row.value_min == requirement_row.value_min


def _text_accepts(info_row, requirement_row):
    expected = ""
    if requirement_row is not None:
        expected = (requirement_row.value_text or "").strip()
    if not expected or expected == ALL_STR:
        return True
    actual = ""
    if info_row is not None:
        actual = (info_row.value_text or "").strip()
    return actual == expected
