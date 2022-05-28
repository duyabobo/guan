#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor


class SecretHandler(BaseHandler):
    @superMonitor
    def get(self):
        return self.response(
            {
                "title": "关关雎鸠介绍",
                "descList": [
                    "《关关雎鸠》小程序是一款安全的、真实的、免费的、高效的互联网见面产品。",
                    "利用互联网技术，解决了现实生活社交存在的两个问题：时间限制和距离限制，帮助用户认识更合适的异性。",
                    "用户注册后，完善个人信息和见面期望，线上报名见面活动，按时参加，到达指定的餐厅，在前台登记见面时间，直接见面见面。",
                    "为了保证安全、真实、免费、高效的原则，请遵守如下见面规则：",
                    "1，请不要爽约或迟到。",
                    "2，请不要提供虚假信息。",
                    "3，见面时请提供教育、工作等证明材料。",
                    "4，餐厅消费自愿，花费AA。",
                    "5，整个过程，请保管好个人财物。",
                    "6，可带朋友一起参加。",
                ]
            }
        )
