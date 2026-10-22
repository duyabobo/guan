#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""小程序里和见面、个人资料相关的展示文案。只从接口下发，不写进小程序包。"""


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
        "privacyEntry": "隐私说明",
        "privacyTitle": "隐私说明",
        "privacyBody": "点按麦克风后才会开始录音。录音会加密保存，并整理成个人信息和期望，用于匹配。页面上不展示原始录音。你可以随时再说一段，覆盖之前整理出的内容。",
        "privacyConfirm": "知道了",
        "voiceStatus": {
            "idle": "说说你自己和期望",
            "recording": "正在录音，再次点击结束",
            "processing": "正在整理个人信息和期望",
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
        "shareLabel": "安全见面，分享好友",
    }
