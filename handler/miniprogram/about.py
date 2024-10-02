#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor, Response


class AboutHandler(BaseHandler):
    @superMonitor
    def get(self):
        return Response(data={
            "title": "",
            "descList": [
                "《关关雎鸠》小程序是一款线上报名，线下见面的交友产品，具有安全、真实、免费、高效等特点。",
                "利用互联网技术，解决了现实生活社交存在的两个问题：时间限制和距离限制，帮助用户认识更合适的异性。",
                "为了保证见面是安全的、真实的、免费的、高效的，请遵守如下见面规则：",
                "1，见面前，请让朋友知道你的行程计划。",
                "2，见面时，请互相提供身份、教育、工作等证明照片。",
                "3，消费AA，如需赠送礼物，请以便宜实用为主。",
                "4，不欺骗，不撒谎，不隐瞒。",
            ]
        })
