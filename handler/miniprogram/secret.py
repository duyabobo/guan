#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor


class SecretHandler(BaseHandler):
    @superMonitor
    def get(self):
        return self.response(
            {
                "title": "隐私条款",
                "descList": [
                    "根据法律规定，开发者仅处理实现小程序功能所必要的信息。",
                    "为了分辨用户，开发者将在获取你的明示同意后，收集你的微信昵称、头像。",
                    "为了根据地理位置推荐活动，开发者将在获取你的明示同意后，收集你的位置信息。",
                    "为了用户自拍照生成头像，开发者将在获取你的明示同意后，访问你的摄像头。",
                    "为了更好的对用户发送通知，开发者将在获取你的明示同意后，收集你的手机号。"
                ]
            }
        )
