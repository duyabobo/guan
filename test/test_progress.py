#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
单元测试：进展状态计算逻辑（progress status）

测试对象：
  - util/const/progress.py ：常量 + calc_activity_progress + get_bottom_buttons
  - 两个函数均为纯函数，无 DB 依赖，可直接单元测试。
"""
import datetime
import sys
import os

# 确保 guan 目录在 Python 路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import MagicMock

from util.const.progress import (
    PROGRESS_NO_CONFIG, PROGRESS_NOT_SELECTED, PROGRESS_SELECTED,
    PROGRESS_WAIT_MEET, PROGRESS_MET, PROGRESS_AGREE, PROGRESS_DISAGREE,
    PROGRESS_DESC, PROGRESS_SORT_WEIGHT,
    HEART_KIND_BROKEN, HEART_KIND_DOUBLE, HEART_KIND_EMPTY, HEART_KIND_SINGLE, HEART_KIND_SOLID,
    MAX_LIST_LEAD_DAYS,
    calc_activity_progress, calc_list_heart_kind, get_bottom_buttons,
    guanguan_list_sort_key, limit_solid_heart_items, should_show_guanguan_item,
)
from util.const.base import (
    GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_QUIT,
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE
)
from util.const.match import (
    MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITING,
    MODEL_ACTIVITY_STATE_INVITE_SUCCESS
)


# ────────────────────────────────────────────
# 辅助构造 mock activity 对象
# ────────────────────────────────────────────

def make_activity(
    state=MODEL_ACTIVITY_STATE_EMPTY,
    boy_pid=0, girl_pid=0,
    start_time=None,
    boy_result=0, girl_result=0,
):
    a = MagicMock()
    a.state = state
    a.boy_passport_id = boy_pid
    a.girl_passport_id = girl_pid
    a.start_time = start_time or datetime.datetime.now() + datetime.timedelta(days=7)
    a.boy_meet_result = boy_result
    a.girl_meet_result = girl_result
    return a


MY_PID = 100
OTHER_PID = 200


# ────────────────────────────────────────────
# 1. 常量正确性
# ────────────────────────────────────────────

class TestProgressConstants:
    def test_all_statuses_have_desc(self):
        for status in [PROGRESS_NO_CONFIG, PROGRESS_NOT_SELECTED, PROGRESS_SELECTED,
                       PROGRESS_WAIT_MEET, PROGRESS_MET, PROGRESS_AGREE, PROGRESS_DISAGREE]:
            assert status in PROGRESS_DESC, f"缺少 PROGRESS_DESC 中状态 {status} 的文案"

    def test_all_statuses_have_sort_weight(self):
        for status in [PROGRESS_NO_CONFIG, PROGRESS_NOT_SELECTED, PROGRESS_SELECTED,
                       PROGRESS_WAIT_MEET, PROGRESS_MET, PROGRESS_AGREE, PROGRESS_DISAGREE]:
            assert status in PROGRESS_SORT_WEIGHT

    def test_sort_weight_order(self):
        """优先级：AGREE/DISAGREE > MET > WAIT_MEET > SELECTED > NOT_SELECTED > NO_CONFIG"""
        assert PROGRESS_SORT_WEIGHT[PROGRESS_AGREE] > PROGRESS_SORT_WEIGHT[PROGRESS_MET]
        assert PROGRESS_SORT_WEIGHT[PROGRESS_DISAGREE] > PROGRESS_SORT_WEIGHT[PROGRESS_MET]
        assert PROGRESS_SORT_WEIGHT[PROGRESS_MET] > PROGRESS_SORT_WEIGHT[PROGRESS_WAIT_MEET]
        assert PROGRESS_SORT_WEIGHT[PROGRESS_WAIT_MEET] > PROGRESS_SORT_WEIGHT[PROGRESS_SELECTED]
        assert PROGRESS_SORT_WEIGHT[PROGRESS_SELECTED] > PROGRESS_SORT_WEIGHT[PROGRESS_NOT_SELECTED]
        assert PROGRESS_SORT_WEIGHT[PROGRESS_NOT_SELECTED] > PROGRESS_SORT_WEIGHT[PROGRESS_NO_CONFIG]


# ────────────────────────────────────────────
# 2. calc_activity_progress（纯函数测试）
# ────────────────────────────────────────────

class TestCalcActivityProgress:

    def test_not_participant_returns_not_selected(self):
        activity = make_activity(state=MODEL_ACTIVITY_STATE_EMPTY, boy_pid=0, girl_pid=0)
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_NOT_SELECTED

    def test_other_participant_returns_not_selected(self):
        """活动已有邀请人，但不是自己"""
        activity = make_activity(state=MODEL_ACTIVITY_STATE_INVITING, boy_pid=OTHER_PID, girl_pid=0)
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_NOT_SELECTED

    def test_single_participant_returns_selected(self):
        activity = make_activity(state=MODEL_ACTIVITY_STATE_INVITING, boy_pid=MY_PID, girl_pid=0)
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_SELECTED

    def test_single_participant_girl_returns_selected(self):
        activity = make_activity(state=MODEL_ACTIVITY_STATE_INVITING, boy_pid=0, girl_pid=MY_PID)
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_SELECTED

    def test_both_joined_future_time_returns_wait_meet(self):
        future = datetime.datetime.now() + datetime.timedelta(days=3)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=future
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_WAIT_MEET

    def test_met_both_unknown_result(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past, boy_result=0, girl_result=0
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_MET

    def test_agree_both_fit(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past,
            boy_result=MODEL_MEET_RESULT_FIT_CHOICE,
            girl_result=MODEL_MEET_RESULT_FIT_CHOICE,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_AGREE

    def test_disagree_my_unfit(self):
        """自己选了不合适"""
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past,
            boy_result=MODEL_MEET_RESULT_UNFIT_CHOICE,
            girl_result=MODEL_MEET_RESULT_FIT_CHOICE,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_DISAGREE

    def test_disagree_opposite_unfit(self):
        """对方选了不合适"""
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past,
            boy_result=MODEL_MEET_RESULT_FIT_CHOICE,
            girl_result=MODEL_MEET_RESULT_UNFIT_CHOICE,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_DISAGREE

    def test_disagree_both_unfit(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past,
            boy_result=MODEL_MEET_RESULT_UNFIT_CHOICE,
            girl_result=MODEL_MEET_RESULT_UNFIT_CHOICE,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_DISAGREE

    def test_met_partial_result_only_me(self):
        """自己已选择合适，对方尚未选择 → 已见面"""
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past,
            boy_result=MODEL_MEET_RESULT_FIT_CHOICE,
            girl_result=0,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_MET

    def test_met_partial_result_only_opposite(self):
        """对方已选择合适，自己尚未选择 → 已见面"""
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=MY_PID, girl_pid=OTHER_PID,
            start_time=past,
            boy_result=0,
            girl_result=MODEL_MEET_RESULT_FIT_CHOICE,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_MET

    def test_as_girl_perspective(self):
        """以女方视角判断，双方合适 → AGREE"""
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        activity = make_activity(
            state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            boy_pid=OTHER_PID, girl_pid=MY_PID,
            start_time=past,
            boy_result=MODEL_MEET_RESULT_FIT_CHOICE,
            girl_result=MODEL_MEET_RESULT_FIT_CHOICE,
        )
        assert calc_activity_progress(MY_PID, activity) == PROGRESS_AGREE


# ────────────────────────────────────────────
# 3. get_bottom_buttons（纯函数测试）
# ────────────────────────────────────────────

class TestGetBottomButtons:

    def test_not_selected_invite_shows_initiate(self):
        buttons = get_bottom_buttons(PROGRESS_NOT_SELECTED, GUAN_INFO_OP_TYPE_INVITE)
        assert len(buttons) == 1
        assert buttons[0]['label'] == '发起见面'
        assert buttons[0]['action'] == 'operate'
        assert buttons[0]['needConfirm'] is False

    def test_not_selected_join_shows_meet(self):
        buttons = get_bottom_buttons(PROGRESS_NOT_SELECTED, GUAN_INFO_OP_TYPE_JOIN)
        assert buttons[0]['label'] == '见面'
        assert buttons[0]['needConfirm'] is False

    def test_selected_shows_cancel_with_confirm(self):
        buttons = get_bottom_buttons(PROGRESS_SELECTED, GUAN_INFO_OP_TYPE_QUIT)
        assert len(buttons) == 1
        assert buttons[0]['label'] == '取消'
        assert buttons[0]['opType'] == GUAN_INFO_OP_TYPE_QUIT
        assert buttons[0]['needConfirm'] is True

    def test_wait_meet_shows_cancel_with_confirm(self):
        buttons = get_bottom_buttons(PROGRESS_WAIT_MEET, GUAN_INFO_OP_TYPE_QUIT)
        assert buttons[0]['label'] == '取消'
        assert buttons[0]['needConfirm'] is True

    def test_met_shows_fit_and_unfit(self):
        buttons = get_bottom_buttons(PROGRESS_MET, GUAN_INFO_OP_TYPE_QUIT)
        labels = {b['label'] for b in buttons}
        assert '合适' in labels
        assert '不合适' in labels
        assert len(buttons) == 2
        assert all(b['needConfirm'] for b in buttons)

    def test_met_buttons_correct_values(self):
        buttons = get_bottom_buttons(PROGRESS_MET, GUAN_INFO_OP_TYPE_QUIT)
        fit_btn = next(b for b in buttons if b['label'] == '合适')
        unfit_btn = next(b for b in buttons if b['label'] == '不合适')
        assert fit_btn['value'] == MODEL_MEET_RESULT_FIT_CHOICE
        assert unfit_btn['value'] == MODEL_MEET_RESULT_UNFIT_CHOICE

    def test_agree_shows_end_relationship(self):
        buttons = get_bottom_buttons(PROGRESS_AGREE, GUAN_INFO_OP_TYPE_QUIT)
        assert len(buttons) == 1
        assert buttons[0]['label'] == '结束关系'
        assert buttons[0]['value'] == MODEL_MEET_RESULT_UNFIT_CHOICE
        assert buttons[0]['needConfirm'] is True

    def test_disagree_shows_restore_relationship(self):
        buttons = get_bottom_buttons(PROGRESS_DISAGREE, GUAN_INFO_OP_TYPE_QUIT)
        assert len(buttons) == 1
        assert buttons[0]['label'] == '恢复关系'
        assert buttons[0]['value'] == MODEL_MEET_RESULT_FIT_CHOICE
        assert buttons[0]['needConfirm'] is True

    def test_no_config_returns_empty(self):
        buttons = get_bottom_buttons(PROGRESS_NO_CONFIG, GUAN_INFO_OP_TYPE_INVITE)
        assert buttons == []


# ────────────────────────────────────────────
# 4. 列表排序逻辑
# ────────────────────────────────────────────

class TestGuanguanListSorting:

    def test_sort_order_full(self):
        """全状态排序：AGREE/DISAGREE 最高，NOT_SELECTED 最低"""
        pairs = [
            (None, PROGRESS_NOT_SELECTED),
            (None, PROGRESS_AGREE),
            (None, PROGRESS_MET),
            (None, PROGRESS_SELECTED),
            (None, PROGRESS_WAIT_MEET),
            (None, PROGRESS_DISAGREE),
        ]
        pairs.sort(key=lambda x: PROGRESS_SORT_WEIGHT.get(x[1], 0), reverse=True)
        sorted_statuses = [p for _, p in pairs]

        assert sorted_statuses[0] in (PROGRESS_AGREE, PROGRESS_DISAGREE)
        assert sorted_statuses[1] in (PROGRESS_AGREE, PROGRESS_DISAGREE)
        assert sorted_statuses[-1] == PROGRESS_NOT_SELECTED

    def test_agree_and_disagree_both_before_met(self):
        pairs = [
            (None, PROGRESS_MET),
            (None, PROGRESS_AGREE),
            (None, PROGRESS_DISAGREE),
        ]
        pairs.sort(key=lambda x: PROGRESS_SORT_WEIGHT[x[1]], reverse=True)
        top_two_statuses = {p for _, p in pairs[:2]}
        assert top_two_statuses == {PROGRESS_AGREE, PROGRESS_DISAGREE}

    def test_wait_meet_before_selected(self):
        assert PROGRESS_SORT_WEIGHT[PROGRESS_WAIT_MEET] > PROGRESS_SORT_WEIGHT[PROGRESS_SELECTED]

    def test_selected_before_not_selected(self):
        assert PROGRESS_SORT_WEIGHT[PROGRESS_SELECTED] > PROGRESS_SORT_WEIGHT[PROGRESS_NOT_SELECTED]


class TestGuanguanHeartKind:

    def test_heart_kind_mapping(self):
        assert calc_list_heart_kind(PROGRESS_DISAGREE) == HEART_KIND_BROKEN
        assert calc_list_heart_kind(PROGRESS_AGREE) == HEART_KIND_SOLID
        assert calc_list_heart_kind(PROGRESS_MET) == HEART_KIND_SOLID
        assert calc_list_heart_kind(PROGRESS_WAIT_MEET) == HEART_KIND_DOUBLE
        assert calc_list_heart_kind(PROGRESS_SELECTED) == HEART_KIND_SINGLE
        assert calc_list_heart_kind(PROGRESS_NOT_SELECTED, has_match=True) == HEART_KIND_SINGLE
        assert calc_list_heart_kind(PROGRESS_NOT_SELECTED, has_match=False) == HEART_KIND_EMPTY

    def test_hide_items_beyond_two_weeks(self):
        assert should_show_guanguan_item(HEART_KIND_EMPTY, 5, MAX_LIST_LEAD_DAYS * 24 * 60) is False
        assert should_show_guanguan_item(HEART_KIND_SINGLE, 5, MAX_LIST_LEAD_DAYS * 24 * 60 + 1) is False
        assert should_show_guanguan_item(HEART_KIND_SOLID, 5, MAX_LIST_LEAD_DAYS * 24 * 60 + 999) is True

    def test_empty_item_time_window_by_distance(self):
        assert should_show_guanguan_item(HEART_KIND_EMPTY, 5, 50) is True
        assert should_show_guanguan_item(HEART_KIND_EMPTY, 5, 90) is False
        assert should_show_guanguan_item(HEART_KIND_EMPTY, 15, 110) is True
        assert should_show_guanguan_item(HEART_KIND_EMPTY, 15, 130) is False

    def test_only_one_solid_heart_in_list(self):
        items = [
            ("solid", 1),
            ("solid", 2),
            ("broken", 3),
        ]
        limited = limit_solid_heart_items(items, lambda item: item[0])
        assert [item[0] for item in limited] == ["solid", "broken"]

    def test_permanent_hearts_always_show(self):
        now = datetime.datetime.now()
        future = now + datetime.timedelta(days=30)
        for kind in (HEART_KIND_BROKEN, HEART_KIND_SOLID, HEART_KIND_DOUBLE):
            assert should_show_guanguan_item(kind, 50, 99999) is True
            assert guanguan_list_sort_key(kind, 50, future, now)[0] < guanguan_list_sort_key(
                HEART_KIND_EMPTY, 1, future, now
            )[0]
