#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""见面提醒。文案长度按微信订阅消息 thing 的上限截断。全部走小程序订阅消息。"""
import datetime

# 小程序里已经申请的订阅模板。字段名可在 weixin 配置里覆盖。
SUBSCRIBE_TEMPLATE_ID = '0LeRGd69AHugmAOYDLHxut1DBZhpkZUdZb5f57DeD3g'
SUBSCRIBE_ACCEPT = 'accept'
SUBSCRIBE_FIELD_TITLE = 'thing1'
SUBSCRIBE_FIELD_TIME = 'time2'
SUBSCRIBE_FIELD_NOTE = 'thing3'
THING_MAX_LEN = 20
SUBSCRIBE_REMAIN_CAP = 20


def clip_thing(text):
    text = text or ''
    if len(text) <= THING_MAX_LEN:
        return text
    return text[:THING_MAX_LEN]

SCENE_JOINED = 'joined'
SCENE_CANCELLED = 'cancelled'
SCENE_DECIDE = 'decide'
SCENE_MEET_SOON = 'meet_soon'
SCENE_LIST_EXPIRE = 'list_expire'
SCENE_NO_SHOW = 'no_show'
SCENE_UNFIT = 'unfit'

_CN_DIGIT = '零一二三四五六七八九'
BOSS_GREETING = '你好老板，我%s约了人'

NOTICE_TEXT = {
    SCENE_JOINED: ('有人加入了见面', '请按时到达约定地点'),
    SCENE_CANCELLED: ('对方取消了见面', '对方已离开，座位已退回'),
    SCENE_DECIDE: ('请尽快决定是否合适', '未选满7天会视为合适'),
    SCENE_MEET_SOON: ('见面时间快到了', '和老板打个招呼'),
    SCENE_LIST_EXPIRE: ('这场快从列表消失', '还没有人加入这场见面'),
    SCENE_NO_SHOW: ('已记录爽约', '之后按爽约次数付费'),
    SCENE_UNFIT: ('对方选择了不合适', '打开详情可以查看'),
}


def _cn_number(value):
    if value < 10:
        return _CN_DIGIT[value]
    if value < 20:
        if value == 10:
            return '十'
        return '十' + _CN_DIGIT[value - 10]
    tens, ones = divmod(value, 10)
    text = _CN_DIGIT[tens] + '十'
    if ones:
        text += _CN_DIGIT[ones]
    return text


def boss_clock(start_time):
    """见面钟点，说给店老板听。十点、十点半，或十点十五分。"""
    hour = _cn_number(start_time.hour)
    if start_time.minute == 0:
        return '%s点' % hour
    if start_time.minute == 30:
        return '%s点半' % hour
    return '%s点%s分' % (hour, _cn_number(start_time.minute))


def boss_greeting(start_time):
    return BOSS_GREETING % boss_clock(start_time)


def notice_sms_text(scene, start_time, note=''):
    """订阅发不出去时的短信。见面那条仍用和老板打招呼的句子。"""
    title, default_note = NOTICE_TEXT.get(scene, ('', ''))
    shown = _sms_note(scene, start_time, note, default_note)
    clock = start_time.strftime('%m月%d日 %H:%M') if start_time else ''
    return '关关雎鸠：%s。%s。%s' % (title, clock, shown)


def _sms_note(scene, start_time, note, default_note):
    if scene == SCENE_MEET_SOON and start_time:
        return boss_greeting(start_time)
    return note or default_note

MEET_SOON_LEAD = datetime.timedelta(minutes=60)
LIST_EXPIRE_LEAD = datetime.timedelta(minutes=15)
SCAN_INTERVAL_MS = 60 * 1000
SCAN_LOCK_SEC = 120
SCAN_ACTIVITY_LIMIT = 200
NOTICE_SCAN_LOCK_KEY = 'notice_scan'
ACCESS_TOKEN_SKEW_SEC = 120
WX_HTTP_TIMEOUT_SEC = 5
MINIPROGRAM_STATE_FORMAL = 'formal'
MINIPROGRAM_STATE_DEVELOPER = 'developer'
ONLINE_SERVER = 'online'

MEET_PAGE = 'page/guan_info/guan_info?guanId=%s'
WX_TOKEN_CACHE_KEY = 'wx_mini_access_token'
