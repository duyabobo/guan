#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""小程序里和见面、个人资料相关的展示文案。只从接口下发，不写进小程序包。"""
from service.common.phone_number import PHONE_CODE_LENGTH, PHONE_DIGIT_COUNT


def list_page_copy():
    return {
        "listTitle": "见面",
    }


def match_config_copy():
    return {
        "pageTitle": "关关雎鸠",
        "transcriptLabel": "刚才说的",
        "infoTitle": "我的信息",
        "requirementTitle": "我的期望",
        "emptyText": "说一段话后，这里会整理出个人信息和期望",
        "voiceBlockTitle": "暂时不能录音",
        "profileConflictTitle": "已保留原资料",
        "voiceRejectTitle": "暂时不能更新",
        "privacyEntry": "隐私说明",
        "privacyTitle": "隐私说明",
        "privacyBody": "点按麦克风后才会开始录音。录音会加密保存，并整理成个人信息和期望，用于匹配。页面上不展示原始录音。性别、身高、出生年份和籍贯确认后，不能再用语音改掉；新的说法和原来不一致时，会保留原来的，并等待人工客服确认。已经约好见面，或已经选了合适之后，不能再录音。目前只支持找异性。",
        "privacyConfirm": "知道了",
        "voiceStatus": {
            "idle": "说说你自己和想找的人",
            "recording": "正在录音，再次点击结束",
            "processing": "正在解析，完成后会自动更新",
        },
        "micDeniedTitle": "需要麦克风",
        "micDeniedContent": "语音搜集需要使用麦克风，请在设置里允许录音。",
        "micDeniedConfirm": "去设置",
    }


def guan_info_copy():
    return {
        "pageTitle": "见面详情",
        "infoTitle": "ta的信息",
        "requirementTitle": "ta的期望",
        "emptyText": "还没有可展示的对象资料",
        "shareLabel": "安全见面，分享亲友",
        "phoneGateTitle": "绑定手机号",
        "phonePlaceholder": "手机号",
        "codePlaceholder": "验证码",
        "sendCodeButton": "获取验证码",
        "phoneGateButton": "完成",
        "phoneGateLater": "先看看",
        "phoneDigitCount": PHONE_DIGIT_COUNT,
        "codeLength": PHONE_CODE_LENGTH,
    }
