#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""小程序订阅消息。access_token 放 Redis，不写进日志。"""
import logging

from util.config import get_conf
from util.const.notice import (
    ACCESS_TOKEN_SKEW_SEC,
    MINIPROGRAM_STATE_DEVELOPER,
    MINIPROGRAM_STATE_FORMAL,
    ONLINE_SERVER,
    SUBSCRIBE_FIELD_NOTE,
    SUBSCRIBE_FIELD_TIME,
    SUBSCRIBE_FIELD_TITLE,
    SCENE_MEET_SOON,
    SUBSCRIBE_TEMPLATE_ID,
    WX_HTTP_TIMEOUT_SEC,
    boss_greeting,
    WX_TOKEN_CACHE_KEY,
    clip_thing,
)
from util.redis_conn import decode_redis_value, redisConn
from util.wx_http import post_json, read_json

logger = logging.getLogger(__name__)

_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
_SEND_URL = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send'


def template_id():
    configured = get_conf('subscribe_template_id', SUBSCRIBE_TEMPLATE_ID, 'weixin')
    return configured or SUBSCRIBE_TEMPLATE_ID


def field_names():
    return (
        get_conf('subscribe_field_title', SUBSCRIBE_FIELD_TITLE, 'weixin') or SUBSCRIBE_FIELD_TITLE,
        get_conf('subscribe_field_time', SUBSCRIBE_FIELD_TIME, 'weixin') or SUBSCRIBE_FIELD_TIME,
        get_conf('subscribe_field_note', SUBSCRIBE_FIELD_NOTE, 'weixin') or SUBSCRIBE_FIELD_NOTE,
    )


def build_data(scene, start_time, text_map, note=''):
    title, default_note = text_map[scene]
    if note:
        shown = note
    elif scene == SCENE_MEET_SOON:
        shown = boss_greeting(start_time)
    else:
        shown = default_note
    title_key, time_key, note_key = field_names()
    return {
        title_key: {'value': clip_thing(title)},
        time_key: {'value': start_time.strftime('%Y年%m月%d日 %H:%M')},
        note_key: {'value': clip_thing(shown)},
    }


def miniprogram_state():
    server = get_conf('server', '', 'global')
    if server == ONLINE_SERVER:
        return MINIPROGRAM_STATE_FORMAL
    return MINIPROGRAM_STATE_DEVELOPER


def app_credentials():
    return get_conf('appid', '', 'weixin'), get_conf('secret', '', 'weixin')


def access_token():
    cached = decode_redis_value(redisConn.get(WX_TOKEN_CACHE_KEY))
    if cached:
        return cached
    appid, secret = app_credentials()
    if not appid or not secret:
        logger.info("订阅消息未取 token，缺少小程序 appid 或 secret")
        return ''
    url = '%s?grant_type=client_credential&appid=%s&secret=%s' % (_TOKEN_URL, appid, secret)
    payload = read_json(url, WX_HTTP_TIMEOUT_SEC)
    token = payload.get('access_token') or ''
    expires = int(payload.get('expires_in') or 0)
    if not token or expires <= ACCESS_TOKEN_SKEW_SEC:
        logger.info("订阅消息未取到 token err=%s", payload.get('errcode'))
        return ''
    redisConn.set(WX_TOKEN_CACHE_KEY, token, ex=expires - ACCESS_TOKEN_SKEW_SEC)
    return token


def send_subscribe(openid, template, page, data, state):
    """发给一个 openid。失败只记错误码，返回是否被微信接受。"""
    token = access_token()
    if not token or not openid or not template:
        logger.info("订阅消息未发送，token、openid 或模板为空")
        return False
    url = '%s?access_token=%s' % (_SEND_URL, token)
    payload = {
        'touser': openid,
        'template_id': template,
        'page': page,
        'miniprogram_state': state,
        'lang': 'zh_CN',
        'data': data,
    }
    try:
        result = post_json(url, payload, WX_HTTP_TIMEOUT_SEC)
    except Exception:
        logger.exception("订阅消息发送失败")
        return False
    errcode = result.get('errcode')
    if errcode:
        logger.info("订阅消息被微信拒绝 errcode=%s", errcode)
        return False
    return True
