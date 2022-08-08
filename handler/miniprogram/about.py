#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor


class AboutHandler(BaseHandler):
    @superMonitor
    def get(self):
        return self.response(
            {
                "title": "",
                "descList": [
                    "《关关雎鸠》小程序是一款安全的、真实的、免费的、高效的互联网见面产品。",
                    "利用互联网技术，解决了现实生活社交存在的两个问题：时间限制和距离限制，帮助用户认识更合适的异性。",
                    "用户注册后，完善个人信息和见面期望，线上报名，线下见面。",
                    "为了保证见面是安全的、真实的、免费的、高效的，请遵守如下见面规则：",
                    "1，见面前，请让朋友知道你的计划。",
                    "2，见面时，请互相提供教育、工作等证明照片。",
                    "3，建议消费AA制，如需赠送礼物便宜实用为主。",
                    "4，不欺骗，不撒谎，不隐瞒。",
                ]
            }
        )
