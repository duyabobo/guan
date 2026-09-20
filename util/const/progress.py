#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户在见面活动中的进展状态枚举
以及两个纯函数：calc_activity_progress / get_bottom_buttons
（无 DB 依赖，可直接单元测试）
"""
import datetime

from util.const.base import (
    GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_QUIT,
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE
)
from util.const.match import (
    MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_INVITE_SUCCESS
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
