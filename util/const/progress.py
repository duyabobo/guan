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
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE, MODEL_MEET_RESULT_UNKNOWN
)
from util.const.match import (
    MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
)

# PROGRESS_STATUS - 进展状态常量
PROGRESS_NO_CONFIG = -1   # 匹配配置不足，需完善信息
PROGRESS_NOT_SELECTED = 0  # 尚未选择
PROGRESS_SELECTED = 1      # 已选择（等待对方确认）
PROGRESS_WAIT_MEET = 2     # 双边确认，等待见面
PROGRESS_MET = 3           # 一方已选合适，双方都是半实心
PROGRESS_AGREE = 4         # 双方都选合适，全实心
PROGRESS_DISAGREE = 5      # 不同意交往（有一方选不合适）

# 进展状态文案
PROGRESS_DESC = {
    PROGRESS_NO_CONFIG: "待配置",
    PROGRESS_NOT_SELECTED: "待选择",
    PROGRESS_SELECTED: "等待中",
    PROGRESS_WAIT_MEET: "待见面",
    PROGRESS_MET: "待确认",
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


# 见面开始后先保持约见面。满 1 小时才能选合适/不合适，满 7 天仍未选则视为合适。
MEET_CHOICE_WAIT = datetime.timedelta(hours=1)
MEET_AUTO_FIT_WAIT = datetime.timedelta(days=7)
UNFIT_SYNC_HINT = "这个结果会同步给对方，并通知对方"
HALF_FIT_HINT = "双方都会变成半实心，对方也选合适后变成实心"


def _results_unset(activity):
    return not activity.boy_meet_result and not activity.girl_meet_result


def meet_choice_ready(activity, now=None):
    """见面开始满 1 小时后，才出现合适/不合适。"""
    now = now or datetime.datetime.now()
    if not activity or not activity.start_time:
        return False
    return now >= activity.start_time + MEET_CHOICE_WAIT


def meet_auto_fit_due(activity, now=None):
    """双方都没表态，且见面开始已满 7 天。"""
    now = now or datetime.datetime.now()
    if not activity or activity.state != MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
        return False
    if not _results_unset(activity) or not activity.start_time:
        return False
    return now >= activity.start_time + MEET_AUTO_FIT_WAIT


def calc_activity_progress(passport_id, activity, now=None):
    """
    纯函数：根据 passportId 和 activity 计算进展状态。
    不依赖任何 DB，可直接单元测试。

    双方都还没选合适或不合适时，一直是约见面（双心）。
    只有一方选了合适，双方都是半实心。双方都选了，才是全实心。
    任何一方不合适，双方都是心碎，盖过对方的合适。
    满 7 天仍未选，按双方合适处理。
    """
    now = now or datetime.datetime.now()
    is_participant = passport_id in (activity.boy_passport_id, activity.girl_passport_id)
    if not is_participant:
        return PROGRESS_NOT_SELECTED

    if activity.state == MODEL_ACTIVITY_STATE_INVITING:
        return PROGRESS_SELECTED

    if activity.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
        if _results_unset(activity):
            if meet_auto_fit_due(activity, now):
                return PROGRESS_AGREE
            return PROGRESS_WAIT_MEET

        is_boy = passport_id == activity.boy_passport_id
        my_result = activity.boy_meet_result if is_boy else activity.girl_meet_result
        opp_result = activity.girl_meet_result if is_boy else activity.boy_meet_result

        if my_result >= MODEL_MEET_RESULT_UNFIT_CHOICE or opp_result >= MODEL_MEET_RESULT_UNFIT_CHOICE:
            return PROGRESS_DISAGREE
        if my_result == MODEL_MEET_RESULT_FIT_CHOICE and opp_result == MODEL_MEET_RESULT_FIT_CHOICE:
            return PROGRESS_AGREE
        return PROGRESS_MET

    return PROGRESS_NOT_SELECTED


def result_change_allowed(progress_status, meet_result_value, choice_ready):
    """合适、不合适、结束关系、恢复关系。约见面要满 1 小时才能首次表态。"""
    if meet_result_value == MODEL_MEET_RESULT_FIT_CHOICE and progress_status == PROGRESS_DISAGREE:
        return True
    if meet_result_value == MODEL_MEET_RESULT_UNFIT_CHOICE and progress_status == PROGRESS_AGREE:
        return True
    if progress_status == PROGRESS_WAIT_MEET and choice_ready:
        return meet_result_value in (MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE)
    if progress_status == PROGRESS_MET:
        return meet_result_value in (MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE)
    return False


STYLE_MEET = "meet"
STYLE_START_MEET = "start-meet"
STYLE_CANCEL = "cancel"
STYLE_SUITABLE = "suitable"
STYLE_UNSUITABLE = "unsuitable"
STYLE_END = "end"
STYLE_RESTORE = "restore"


def _button(label, action, style_key, need_confirm, op_type=None, value=None, hint="", ask_subscribe=False):
    button = {
        "label": label,
        "action": action,
        "styleKey": style_key,
        "needConfirm": need_confirm,
    }
    if op_type is not None:
        button["opType"] = op_type
    if value is not None:
        button["value"] = value
    if hint:
        button["hint"] = hint
    if ask_subscribe:
        button["askSubscribe"] = True
    return button


def quit_is_allowed(progress_status, choice_ready=False):
    """发出邀请后可以取消。约见面在出现合适/不合适之前也可以取消。"""
    if progress_status == PROGRESS_SELECTED:
        return True
    return progress_status == PROGRESS_WAIT_MEET and not choice_ready


HOLD_APPOINTMENT = "appointment"
HOLD_FIT = "fit"
OP_TOWARD_MEET = "toward_meet"
OP_CHOOSE_FIT = "choose_fit"


def fit_marks_only_self(progress_status, meet_result_value):
    """合适和恢复关系都只记自己。一方合适是半实心，双方都合适才是全实心。"""
    if meet_result_value != MODEL_MEET_RESULT_FIT_CHOICE:
        return False
    return progress_status in (PROGRESS_WAIT_MEET, PROGRESS_MET, PROGRESS_DISAGREE)


def _without_unfit(result):
    if result >= MODEL_MEET_RESULT_UNFIT_CHOICE:
        return MODEL_MEET_RESULT_UNKNOWN
    return result or 0


def next_results_after_my_fit(boy_result, girl_result, actor_is_boy):
    """自己标合适。对方如果还是不合适，先清成未表态，已经合适的保持。"""
    if actor_is_boy:
        return MODEL_MEET_RESULT_FIT_CHOICE, _without_unfit(girl_result)
    return _without_unfit(boy_result), MODEL_MEET_RESULT_FIT_CHOICE


def relationship_hold(passport_id, activity):
    """一场见面占住的名额。约见面=双方已确认且还没表态。半心和全心一样，都算已经进入合适。"""
    progress = calc_activity_progress(passport_id, activity)
    if progress == PROGRESS_WAIT_MEET:
        return HOLD_APPOINTMENT
    if progress in (PROGRESS_MET, PROGRESS_AGREE):
        return HOLD_FIT
    return ""


def hold_block_reason(op, has_appointment, has_fit):
    """已有约见面时，不能再约，也不能做约见面之前的发起和加入。
    已有半心或全心时，不能再选合适，也不能做合适之前的约见面、发起和加入。
    """
    if has_fit and op in (OP_TOWARD_MEET, OP_CHOOSE_FIT):
        return HOLD_FIT
    if has_appointment and op == OP_TOWARD_MEET:
        return HOLD_APPOINTMENT
    return ""


def _unfit_button():
    return _button(
        "不合适", "meetResult", STYLE_UNSUITABLE, True,
        value=MODEL_MEET_RESULT_UNFIT_CHOICE, hint=UNFIT_SYNC_HINT,
    )


def _fit_buttons():
    return [
        _button(
            "合适", "meetResult", STYLE_SUITABLE, True,
            value=MODEL_MEET_RESULT_FIT_CHOICE, hint=HALF_FIT_HINT, ask_subscribe=True,
        ),
        _unfit_button(),
    ]


def get_bottom_buttons(progress_status, op_type, choice_ready=False, my_result=0):
    """
    纯函数：根据进展状态和操作类型，返回底部按钮配置列表。
    不依赖任何 DB，可直接单元测试。

    :param progress_status: PROGRESS_* 常量
    :param op_type:         GUAN_INFO_OP_TYPE_* 常量（仅 NOT_SELECTED 时使用）
    :return: list of dict {label, action, styleKey, needConfirm, ...}
    """
    if progress_status == PROGRESS_NOT_SELECTED:
        if op_type == GUAN_INFO_OP_TYPE_INVITE:
            return [_button("发起见面", "operate", STYLE_START_MEET, False, op_type=op_type, ask_subscribe=True)]
        return [_button("见面", "operate", STYLE_MEET, False, op_type=op_type, ask_subscribe=True)]

    if progress_status == PROGRESS_WAIT_MEET and choice_ready:
        return _fit_buttons()

    if quit_is_allowed(progress_status, choice_ready):
        return [_button("取消", "operate", STYLE_CANCEL, True, op_type=GUAN_INFO_OP_TYPE_QUIT)]

    if progress_status == PROGRESS_MET:
        if my_result == MODEL_MEET_RESULT_FIT_CHOICE:
            return [_unfit_button()]
        return _fit_buttons()

    if progress_status == PROGRESS_AGREE:
        return [_button("结束关系", "meetResult", STYLE_END, True,
                        value=MODEL_MEET_RESULT_UNFIT_CHOICE, hint=UNFIT_SYNC_HINT)]

    if progress_status == PROGRESS_DISAGREE:
        return [_button(
            "恢复关系", "meetResult", STYLE_RESTORE, True,
            value=MODEL_MEET_RESULT_FIT_CHOICE, hint=HALF_FIT_HINT, ask_subscribe=True,
        )]

    return []  # PROGRESS_NO_CONFIG 或其他异常状态


# 分享出去的见面页：1 表示观众打开，只能看
MEET_VIEWER_MODE = 1


def build_meet_share_guide(progress_status, label, viewer):
    """双心（待见面）才出现安全见面分享。观众打开时没有分享，也没有操作。"""
    if viewer or progress_status != PROGRESS_WAIT_MEET:
        return {"enabled": False, "label": ""}
    return {"enabled": True, "label": label}


# ── 首页列表心形标识 ──────────────────────────────────────────────────────────

HEART_KIND_EMPTY = "empty"
HEART_KIND_SINGLE = "single"
HEART_KIND_DOUBLE = "double"
HEART_KIND_HALF = "half"
HEART_KIND_SOLID = "solid"
HEART_KIND_BROKEN = "broken"

PERMANENT_HEART_KINDS = frozenset({
    HEART_KIND_BROKEN,
    HEART_KIND_SOLID,
    HEART_KIND_HALF,
    HEART_KIND_DOUBLE,
})

# 列表排序：实心 > 半实心 > 心碎 > 双心 > 单心 > 无心（再按 10km 距离档、见面时间）
HEART_SORT_ORDER = {
    HEART_KIND_SOLID: 0,
    HEART_KIND_HALF: 1,
    HEART_KIND_BROKEN: 2,
    HEART_KIND_DOUBLE: 3,
    HEART_KIND_SINGLE: 4,
    HEART_KIND_EMPTY: 5,
}

DISTANCE_BUCKET_KM = 10
LIST_WINDOW_DAYS = 14
LIST_WINDOW_MINUTES = LIST_WINDOW_DAYS * 24 * 60
MAX_LIST_DISTANCE_KM = 100
MINUTES_PER_HOUR = 60
LEAD_HOURS_PER_DISTANCE_BUCKET = 1
LEAD_MINUTES_PER_DISTANCE_BUCKET = LEAD_HOURS_PER_DISTANCE_BUCKET * MINUTES_PER_HOUR
MAX_TRANSIENT_LEAD_MINUTES = int(
    math.ceil(MAX_LIST_DISTANCE_KM / float(DISTANCE_BUCKET_KM)) * LEAD_MINUTES_PER_DISTANCE_BUCKET
)
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
    """10 公里一档，整档落在这一档里。10 公里是第 1 档，20 公里是第 2 档。"""
    if distance_km is None:
        return 999
    if distance_km <= DISTANCE_BUCKET_KM:
        return 1
    return math.ceil(distance_km / DISTANCE_BUCKET_KM)


def max_lead_minutes_for_transient(distance_km):
    """还没约上的场次：每 10 公里只能再留 1 小时，超时就从列表拿掉。"""
    return distance_bucket_km(distance_km) * LEAD_MINUTES_PER_DISTANCE_BUCKET


def calc_list_heart_kind(progress_status, has_match=False):
    """
    首页心形：
    - broken：不合适 / 缺席等（progress=DISAGREE）
    - solid：双方都选了合适（AGREE）
    - half：只有一方选了合适（MET）
    - double：双方已约同一见面（WAIT_MEET）
    - single：有匹配异性 / 等待对方确认（SELECTED 或候选匹配）
    - empty：空闲时段
    """
    if progress_status == PROGRESS_DISAGREE:
        return HEART_KIND_BROKEN
    if progress_status == PROGRESS_AGREE:
        return HEART_KIND_SOLID
    if progress_status == PROGRESS_MET:
        return HEART_KIND_HALF
    if progress_status == PROGRESS_WAIT_MEET:
        return HEART_KIND_DOUBLE
    if progress_status == PROGRESS_SELECTED:
        return HEART_KIND_SINGLE
    if progress_status == PROGRESS_NOT_SELECTED:
        return HEART_KIND_SINGLE if has_match else HEART_KIND_EMPTY
    return HEART_KIND_EMPTY


# 语音录入是见面的第一步。双心、半实心、实心说明这步已经过去。
VOICE_BLOCKED_HEART_KINDS = frozenset({
    HEART_KIND_DOUBLE,
    HEART_KIND_HALF,
    HEART_KIND_SOLID,
})


def voice_blocked_by_progress(progress_status):
    return calc_list_heart_kind(progress_status) in VOICE_BLOCKED_HEART_KINDS


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
    """匹配过滤：已参与活动直接展示；候选场次需在资料匹配集合内"""
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
