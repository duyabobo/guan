#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户在见面活动中的进展状态枚举
以及两个纯函数：calc_activity_progress / get_bottom_buttons
（无 DB 依赖，可直接单元测试）
"""
import datetime
import math

from util.const.base import (
    GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_QUIT,
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE
)
from util.const.match import (
    MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
)

# PROGRESS_STATUS - 进展状态常量
PROGRESS_NO_CONFIG = -1   # 匹配配置不足，需完善信息
PROGRESS_NOT_SELECTED = 0  # 尚未选择
PROGRESS_SELECTED = 1      # 已选择（等待对方确认）
PROGRESS_WAIT_MEET = 2     # 双边确认，等待见面
PROGRESS_MET = 3           # 已见面，尚未表达意向
PROGRESS_AGREE = 4         # 已同意交往（双方都选合适）
PROGRESS_DISAGREE = 5      # 不同意交往（有一方选不合适）

# 进展状态文案
PROGRESS_DESC = {
    PROGRESS_NO_CONFIG: "待配置",
    PROGRESS_NOT_SELECTED: "待选择",
    PROGRESS_SELECTED: "等待中",
    PROGRESS_WAIT_MEET: "待见面",
    PROGRESS_MET: "已见面",
    PROGRESS_AGREE: "在一起",
    PROGRESS_DISAGREE: "不合适",
}

# 列表排序权重（数字越大优先级越高）
PROGRESS_SORT_WEIGHT = {
    PROGRESS_AGREE: 60,
    PROGRESS_DISAGREE: 50,
    PROGRESS_MET: 40,
    PROGRESS_WAIT_MEET: 30,
    PROGRESS_SELECTED: 20,
    PROGRESS_NOT_SELECTED: 10,
    PROGRESS_NO_CONFIG: 0,
}

# 需要二次确认的进展状态
PROGRESS_NEED_CONFIRM = frozenset({
    PROGRESS_SELECTED, PROGRESS_WAIT_MEET,
    PROGRESS_MET, PROGRESS_AGREE, PROGRESS_DISAGREE
})


def calc_activity_progress(passport_id, activity):
    """
    纯函数：根据 passportId 和 activity 计算进展状态。
    不依赖任何 DB，可直接单元测试。

    :param passport_id: 当前用户 passport_id
    :param activity:    activity 对象（含 state/boy_pid/girl_pid/start_time/meet_result 等字段）
    :return:            PROGRESS_* 常量
    """
    is_participant = passport_id in (activity.boy_passport_id, activity.girl_passport_id)
    if not is_participant:
        return PROGRESS_NOT_SELECTED

    if activity.state == MODEL_ACTIVITY_STATE_INVITING:
        return PROGRESS_SELECTED

    if activity.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
        if activity.start_time > datetime.datetime.now():
            return PROGRESS_WAIT_MEET

        is_boy = passport_id == activity.boy_passport_id
        my_result = activity.boy_meet_result if is_boy else activity.girl_meet_result
        opp_result = activity.girl_meet_result if is_boy else activity.boy_meet_result

        if my_result == MODEL_MEET_RESULT_FIT_CHOICE and opp_result == MODEL_MEET_RESULT_FIT_CHOICE:
            return PROGRESS_AGREE
        if my_result >= MODEL_MEET_RESULT_UNFIT_CHOICE or opp_result >= MODEL_MEET_RESULT_UNFIT_CHOICE:
            return PROGRESS_DISAGREE
        return PROGRESS_MET

    return PROGRESS_NOT_SELECTED


def get_bottom_buttons(progress_status, op_type):
    """
    纯函数：根据进展状态和操作类型，返回底部按钮配置列表。
    不依赖任何 DB，可直接单元测试。

    :param progress_status: PROGRESS_* 常量
    :param op_type:         GUAN_INFO_OP_TYPE_* 常量（仅 NOT_SELECTED 时使用）
    :return: list of dict {label, action, needConfirm, ...}
    """
    if progress_status == PROGRESS_NOT_SELECTED:
        label = "发起见面" if op_type == GUAN_INFO_OP_TYPE_INVITE else "见面"
        return [{"label": label, "action": "operate", "opType": op_type, "needConfirm": False}]

    if progress_status in (PROGRESS_SELECTED, PROGRESS_WAIT_MEET):
        return [{"label": "取消", "action": "operate", "opType": GUAN_INFO_OP_TYPE_QUIT, "needConfirm": True}]

    if progress_status == PROGRESS_MET:
        return [
            {"label": "合适", "action": "meetResult", "value": MODEL_MEET_RESULT_FIT_CHOICE, "needConfirm": True},
            {"label": "不合适", "action": "meetResult", "value": MODEL_MEET_RESULT_UNFIT_CHOICE, "needConfirm": True},
        ]

    if progress_status == PROGRESS_AGREE:
        return [{"label": "结束关系", "action": "meetResult", "value": MODEL_MEET_RESULT_UNFIT_CHOICE, "needConfirm": True}]

    if progress_status == PROGRESS_DISAGREE:
        return [{"label": "恢复关系", "action": "meetResult", "value": MODEL_MEET_RESULT_FIT_CHOICE, "needConfirm": True}]

    return []  # PROGRESS_NO_CONFIG 或其他异常状态


# ── 首页列表心形标识 ──────────────────────────────────────────────────────────

HEART_KIND_EMPTY = "empty"
HEART_KIND_SINGLE = "single"
HEART_KIND_DOUBLE = "double"
HEART_KIND_SOLID = "solid"
HEART_KIND_BROKEN = "broken"

PERMANENT_HEART_KINDS = frozenset({
    HEART_KIND_BROKEN,
    HEART_KIND_SOLID,
    HEART_KIND_DOUBLE,
})

# 列表排序：实心 > 心碎 > 双心 > 单心 > 无心（再按 10km 距离档、见面时间）
HEART_SORT_ORDER = {
    HEART_KIND_SOLID: 0,
    HEART_KIND_BROKEN: 1,
    HEART_KIND_DOUBLE: 2,
    HEART_KIND_SINGLE: 3,
    HEART_KIND_EMPTY: 4,
}

DISTANCE_BUCKET_KM = 10
LIST_WINDOW_DAYS = 14
LIST_WINDOW_MINUTES = LIST_WINDOW_DAYS * 24 * 60
MAX_LIST_DISTANCE_KM = 100
LEAD_MINUTES_PER_DISTANCE_BUCKET = 120
EARTH_RADIUS_KM = 6371.0


def calc_distance_km(latitude_a, longitude_a, latitude_b, longitude_b):
    if not latitude_a or not longitude_a or not latitude_b or not longitude_b:
        return None
    lat1 = math.radians(latitude_a)
    lat2 = math.radians(latitude_b)
    d_lat = math.radians(latitude_b - latitude_a)
    d_lng = math.radians(longitude_b - longitude_a)
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_bucket_km(distance_km):
    if distance_km is None:
        return 999
    if distance_km <= 0:
        return 1
    return int(distance_km // DISTANCE_BUCKET_KM) + 1


def max_lead_minutes_for_transient(distance_km):
    """单心/空白：每 10km 对应剩余 2 小时内的场次"""
    return distance_bucket_km(distance_km) * LEAD_MINUTES_PER_DISTANCE_BUCKET


def calc_list_heart_kind(progress_status, has_match=False):
    """
    首页心形：
    - broken：不合适 / 缺席等（progress=DISAGREE）
    - solid：已见面且未标不合适（MET/AGREE）
    - double：双方已约同一见面（WAIT_MEET）
    - single：有匹配异性 / 等待对方确认（SELECTED 或候选匹配）
    - empty：空闲时段
    """
    if progress_status == PROGRESS_DISAGREE:
        return HEART_KIND_BROKEN
    if progress_status in (PROGRESS_AGREE, PROGRESS_MET):
        return HEART_KIND_SOLID
    if progress_status == PROGRESS_WAIT_MEET:
        return HEART_KIND_DOUBLE
    if progress_status == PROGRESS_SELECTED:
        return HEART_KIND_SINGLE
    if progress_status == PROGRESS_NOT_SELECTED:
        return HEART_KIND_SINGLE if has_match else HEART_KIND_EMPTY
    return HEART_KIND_EMPTY


def calc_list_has_match(progress_status, activity_state, in_matched_activity_ids):
    """候选场次：空闲=无心；邀请中=单心。已参与场次沿用 Redis 匹配标记。"""
    if progress_status != PROGRESS_NOT_SELECTED:
        return bool(in_matched_activity_ids)
    if activity_state == MODEL_ACTIVITY_STATE_EMPTY:
        return False
    if activity_state == MODEL_ACTIVITY_STATE_INVITING:
        return True
    return bool(in_matched_activity_ids)


def should_show_guanguan_item(heart_kind, distance_km, minutes_until_start):
    if heart_kind in PERMANENT_HEART_KINDS:
        return True
    if distance_km is None or distance_km > MAX_LIST_DISTANCE_KM:
        return False
    if minutes_until_start is None or minutes_until_start < 0:
        return False
    if minutes_until_start > LIST_WINDOW_MINUTES:
        return False
    if heart_kind in (HEART_KIND_EMPTY, HEART_KIND_SINGLE):
        return minutes_until_start <= max_lead_minutes_for_transient(distance_km)
    return False


def should_include_activity_for_match(progress_status, activity_id, activity_state, matched_activity_ids, activity_state_empty):
    """匹配过滤：已参与活动直接展示；候选场次需在 Redis 匹配集合内"""
    if progress_status != PROGRESS_NOT_SELECTED:
        return True
    return activity_id in matched_activity_ids


def limit_solid_heart_items(items, heart_kind_getter):
    """首页实心标识最多展示一条（已排序列表上过滤）"""
    solid_seen = False
    limited = []
    for item in items:
        if heart_kind_getter(item) == HEART_KIND_SOLID:
            if solid_seen:
                continue
            solid_seen = True
        limited.append(item)
    return limited


def guanguan_list_sort_key(heart_kind, distance_km, start_time, now):
    bucket = distance_bucket_km(distance_km)
    if start_time:
        minutes_until = (start_time - now).total_seconds() / 60.0
    else:
        minutes_until = 999999.0
    return (
        HEART_SORT_ORDER.get(heart_kind, 9),
        bucket,
        minutes_until,
    )
