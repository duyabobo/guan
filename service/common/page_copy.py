#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""小程序里和活动、个人资料相关的展示文案。只从接口下发，不写进小程序包。"""
from service.common.phone_number import PHONE_CODE_LENGTH, PHONE_DIGIT_COUNT

_PRIVACY_BODY = (
    "点按麦克风后，未验证手机号将先完成验证。"
    "录音加密保存，并整理为报名信息与参与偏好，用于帮助您找到适合的线下活动；页面不展示原始录音。"
    "性别、身高、出生年月等关键信息一经确认，不能再用语音修改；不一致时保留原信息并转人工确认。"
    "已报名或确认参加后，不能再录音。"
)


def list_page_copy():
    return {
        "listTitle": "活动",
        "entryTitle": "关关雎鸠",
        "shareTitle": "关关雎鸠",
        "showHeart": True,
        "loginHint": "登录后查看",
    }


def phone_gate_copy():
    return {
        "phoneGateTitle": "绑定手机号",
        "phonePlaceholder": "手机号",
        "codePlaceholder": "验证码",
        "sendCodeButton": "获取验证码",
        "phoneGateButton": "完成",
        "phoneGateLater": "先看看",
        "phoneDigitCount": PHONE_DIGIT_COUNT,
        "codeLength": PHONE_CODE_LENGTH,
    }


def match_config_copy():
    copy = {
        "pageTitle": "关关雎鸠",
        "infoTitle": "我的信息",
        "requirementTitle": "我的期望",
        "emptyText": "说一段话后，这里会整理出个人信息和期望",
        "voiceBlockTitle": "暂时不能录音",
        "profileConflictTitle": "已保留原资料",
        "voiceRejectTitle": "暂时不能更新",
        "privacyEntry": "隐私说明",
        "privacyTitle": "隐私说明",
        "privacyBody": _PRIVACY_BODY,
        "privacyConfirm": "知道了",
        "voiceStatus": {
            "idle": "按住说话",
            "recording": "松开发送",
            "recordingCancel": "松开取消",
            "processing": "正在解析，完成后会自动更新",
            "tooShort": "说话时间太短",
        },
        "micDeniedTitle": "需要麦克风",
        "micDeniedContent": "语音搜集需要使用麦克风，请在设置里允许录音。",
        "micDeniedConfirm": "去设置",
    }
    copy.update(phone_gate_copy())
    return copy


def guan_info_copy():
    copy = {
        "pageTitle": "活动详情",
        "infoTitle": "ta的信息",
        "requirementTitle": "ta的期望",
        "emptyText": "还没有可展示的对象资料",
        "shareLabel": "安全活动，分享亲友",
        "shareCardTitle": "安全活动",
        "shareTitle": "关关雎鸠",
    }
    copy.update(phone_gate_copy())
    return copy
